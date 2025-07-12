import React, { useState, useRef, useCallback, useEffect } from 'react';
import { Upload, TrendingUp, BarChart3, Calendar, DollarSign, FileText, AlertCircle, CheckCircle, Download, Zap, Target, Activity } from 'lucide-react';
import * as tf from '@tensorflow/tfjs';

const CompanyProfitPredictor = () => {
  const [file, setFile] = useState(null);
  const [data, setData] = useState([]);
  const [predictions, setPredictions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [stats, setStats] = useState(null);
  const [activeTab, setActiveTab] = useState('upload');
  const [plotlyReady, setPlotlyReady] = useState(false);
  const fileInputRef = useRef(null);
  const plotRef = useRef(null);

  // Load external scripts
  useEffect(() => {
    // Load SheetJS
    const loadScript = (src) => {
      return new Promise((resolve, reject) => {
        const script = document.createElement('script');
        script.src = src;
        script.onload = resolve;
        script.onerror = reject;
        document.head.appendChild(script);
      });
    };

    const loadScripts = async () => {
      try {
        if (!window.XLSX) {
          await loadScript('https://cdn.sheetjs.com/xlsx-latest/package/dist/xlsx.full.min.js');
        }
        if (!window.Plotly) {
          await loadScript('https://cdn.plot.ly/plotly-latest.min.js');
        }
        setPlotlyReady(true);
      } catch (err) {
        setError('Failed to load required libraries');
      }
    };

    loadScripts();
  }, []);

  const handleFileUpload = useCallback((event) => {
    const uploadedFile = event.target.files[0];
    if (!uploadedFile) return;

    if (!uploadedFile.name.endsWith('.xlsx') && !uploadedFile.name.endsWith('.xls')) {
      setError('Please upload an Excel file (.xlsx or .xls)');
      return;
    }

    setFile(uploadedFile);
    setError('');
    setSuccess('File uploaded successfully!');
  }, []);

  const processData = useCallback(async () => {
    if (!file || !window.XLSX) {
      setError('Please upload a file first or wait for libraries to load');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const buffer = await file.arrayBuffer();
      const workbook = window.XLSX.read(buffer, { type: 'array' });
      const sheetName = workbook.SheetNames[0];
      const worksheet = workbook.Sheets[sheetName];
      const jsonData = window.XLSX.utils.sheet_to_json(worksheet);

      // Validate and clean data
      const cleanedData = jsonData.map((row, index) => {
        const date = row.date || row.Date || row.DATE;
        const company = row['company name'] || row['Company Name'] || row.company || row.Company;
        const profit = row.profit || row.Profit || row.PROFIT;

        if (!date || !company || profit === undefined) {
          throw new Error(`Missing required data in row ${index + 1}. Please ensure all rows have date, company name, and profit columns.`);
        }

        // Parse date
        let parsedDate;
        if (typeof date === 'number') {
          // Excel date serial number
          parsedDate = new Date((date - 25569) * 86400 * 1000);
        } else {
          parsedDate = new Date(date);
        }

        if (isNaN(parsedDate.getTime())) {
          throw new Error(`Invalid date format in row ${index + 1}`);
        }

        return {
          date: parsedDate,
          company: company.toString(),
          profit: parseFloat(profit) || 0,
          month: parsedDate.toLocaleDateString('en-US', { year: 'numeric', month: 'short' })
        };
      });

      // Sort by date
      cleanedData.sort((a, b) => a.date - b.date);

      // Generate predictions using TensorFlow.js
      const predictions = await generateTensorFlowPredictions(cleanedData);

      // Calculate statistics
      const statistics = calculateStatistics(cleanedData);

      setData(cleanedData);
      setPredictions(predictions);
      setStats(statistics);
      setActiveTab('analysis');
      setSuccess('Data processed successfully!');

      // Generate plot after data is set
      setTimeout(() => {
        generatePlot(cleanedData, predictions);
      }, 100);

    } catch (err) {
      setError(err.message || 'Error processing file');
    } finally {
      setLoading(false);
    }
  }, [file, plotlyReady]);

  const generateTensorFlowPredictions = async (data) => {
    if (data.length < 2) return [];

    // Group data by company
    const companiesData = {};
    data.forEach(item => {
      if (!companiesData[item.company]) {
        companiesData[item.company] = [];
      }
      companiesData[item.company].push(item);
    });

    const allPredictions = [];

    // Generate predictions for each company using TensorFlow.js
    for (const [company, companyData] of Object.entries(companiesData)) {
      if (companyData.length < 2) continue;

      const sortedData = companyData.sort((a, b) => a.date - b.date);
      
      // Prepare training data
      const xData = sortedData.map((_, index) => index);
      const yData = sortedData.map(item => item.profit);

      // Create tensors
      const xs = tf.tensor2d(xData.map(x => [x]), [xData.length, 1]);
      const ys = tf.tensor2d(yData.map(y => [y]), [yData.length, 1]);

      // Create and compile model
      const model = tf.sequential({
        layers: [
          tf.layers.dense({ units: 10, activation: 'relu', inputShape: [1] }),
          tf.layers.dense({ units: 5, activation: 'relu' }),
          tf.layers.dense({ units: 1 })
        ]
      });

      model.compile({
        optimizer: tf.train.adam(0.1),
        loss: 'meanSquaredError',
        metrics: ['mae']
      });

      // Train the model
      await model.fit(xs, ys, {
        epochs: 100,
        verbose: 0,
        validationSplit: 0.2
      });

      // Generate predictions for next 6 months
      const lastDate = new Date(sortedData[sortedData.length - 1].date);
      
      for (let i = 1; i <= 6; i++) {
        const futureIndex = sortedData.length + i - 1;
        const predictionTensor = model.predict(tf.tensor2d([[futureIndex]], [1, 1]));
        const predictionValue = await predictionTensor.data();
        
        const futureDate = new Date(lastDate);
        futureDate.setMonth(futureDate.getMonth() + i);

        allPredictions.push({
          date: futureDate,
          company: company,
          profit: Math.max(0, predictionValue[0]),
          month: futureDate.toLocaleDateString('en-US', { year: 'numeric', month: 'short' }),
          isPrediction: true
        });

        // Clean up tensors
        predictionTensor.dispose();
      }

      // Clean up tensors
      xs.dispose();
      ys.dispose();
      model.dispose();
    }

    return allPredictions.sort((a, b) => a.date - b.date);
  };

  const calculateStatistics = (data) => {
    if (data.length === 0) return null;

    const profits = data.map(d => d.profit);
    const totalProfit = profits.reduce((a, b) => a + b, 0);
    const avgProfit = totalProfit / profits.length;
    const maxProfit = Math.max(...profits);
    const minProfit = Math.min(...profits);

    // Calculate growth rate
    const firstHalf = profits.slice(0, Math.floor(profits.length / 2));
    const secondHalf = profits.slice(Math.floor(profits.length / 2));
    const firstHalfAvg = firstHalf.reduce((a, b) => a + b, 0) / firstHalf.length;
    const secondHalfAvg = secondHalf.reduce((a, b) => a + b, 0) / secondHalf.length;
    const growthRate = ((secondHalfAvg - firstHalfAvg) / firstHalfAvg) * 100;

    return {
      totalProfit,
      avgProfit,
      maxProfit,
      minProfit,
      growthRate,
      dataPoints: data.length
    };
  };

  const generatePlot = (historicalData, predictedData) => {
    if (!window.Plotly || !plotRef.current) return;

    // Group data by company
    const companiesData = {};
    historicalData.forEach(item => {
      if (!companiesData[item.company]) {
        companiesData[item.company] = { historical: [], predicted: [] };
      }
      companiesData[item.company].historical.push(item);
    });

    predictedData.forEach(item => {
      if (!companiesData[item.company]) {
        companiesData[item.company] = { historical: [], predicted: [] };
      }
      companiesData[item.company].predicted.push(item);
    });

    const traces = [];
    const colors = ['#3b82f6', '#ef4444', '#10b981', '#f59e0b', '#8b5cf6', '#06b6d4', '#f97316', '#84cc16', '#ec4899', '#6366f1'];

    Object.keys(companiesData).forEach((company, index) => {
      const companyData = companiesData[company];
      const color = colors[index % colors.length];

      // Historical data trace
      if (companyData.historical.length > 0) {
        traces.push({
          x: companyData.historical.map(d => d.date.toISOString().split('T')[0]),
          y: companyData.historical.map(d => d.profit),
          mode: 'lines+markers',
          name: `${company} (Historical)`,
          line: { color: color, width: 3 },
          marker: { size: 8, color: color }
        });
      }

      // Predicted data trace
      if (companyData.predicted.length > 0) {
        traces.push({
          x: companyData.predicted.map(d => d.date.toISOString().split('T')[0]),
          y: companyData.predicted.map(d => d.profit),
          mode: 'lines+markers',
          name: `${company} (Predicted)`,
          line: { color: color, width: 2, dash: 'dash' },
          marker: { size: 10, color: color, symbol: 'star' }
        });
      }
    });

    const layout = {
      title: {
        text: 'Company Profit Trends and AI Predictions',
        font: { size: 18, color: '#1f2937' }
      },
      xaxis: { 
        title: 'Date',
        gridcolor: '#e5e7eb',
        tickformat: '%b %Y'
      },
      yaxis: { 
        title: 'Profit ($)',
        gridcolor: '#e5e7eb',
        tickformat: '$,.0f'
      },
      legend: { 
        orientation: 'h',
        y: -0.2,
        x: 0.5,
        xanchor: 'center'
      },
      plot_bgcolor: '#f8fafc',
      paper_bgcolor: '#ffffff',
      margin: { l: 60, r: 30, t: 60, b: 100 }
    };

    window.Plotly.newPlot(plotRef.current, traces, layout, {
      responsive: true,
      displayModeBar: true,
      modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d']
    });
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(value);
  };

  const formatPercentage = (value) => {
    return `${value >= 0 ? '+' : ''}${value.toFixed(1)}%`;
  };

  const companies = [...new Set(data.map(d => d.company))];
  const colors = ['#3b82f6', '#ef4444', '#10b981', '#f59e0b', '#8b5cf6', '#06b6d4', '#f97316', '#84cc16', '#ec4899', '#6366f1'];

  return (
    <div className="min-h-screen"> 
      {/* Header */}
      <div className=" rounded-full bg-white shadow-lg border-b border-slate-200">
        <div className="max-w-7xl  mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex  items-center space-x-3">
              <div className="bg-gradient-to-r from-blue-600 to-indigo-600 p-2 rounded-lg">
                <TrendingUp className="h-8 w-8 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-slate-900">AI Profit Predictor</h1>
                <p className="text-sm text-slate-500">TensorFlow.js Analytics Dashboard</p>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <div className="bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm font-medium">
                AI-Powered
              </div>
              <Zap className="h-5 w-5 text-yellow-500" />
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Tab Navigation */}
        <div className="mb-8">
          <div className="flex space-x-1 bg-white justify-evenly np-1 rounded-lg shadow-sm border border-slate-200">
            <button
              onClick={() => setActiveTab('upload')}
              className={`px-4 py-2  rounded-md font-medium transition-all ${activeTab === 'upload'
                ? 'bg-blue-600 text-white shadow-sm'
                : 'text-slate-100 hover:text-slate-900 hover:bg-slate-50'
                }`}
            >
              <Upload className="h-4 w-4 inline mr-2" />
              Upload New Data
            </button>
            <button
              onClick={() => setActiveTab('analysis')}
              className={`px-4 py-1 rounded-md font-medium transition-all ${activeTab === 'analysis'
                ? 'bg-blue-600 text-white shadow-sm'
                : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
                }`}
              disabled={data.length === 0}
            >
              <BarChart3 className="h-4 w-4 inline mr-2" />
              Analysis & Predictions
            </button>
          </div>
        </div>

        {/* Alert Messages */}
        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4 flex items-center">
            <AlertCircle className="h-5 w-5 text-red-600 mr-3" />
            <span className="text-red-800">{error}</span>
          </div>
        )}

        {success && (
          <div className="mb-6 bg-green-50 border border-green-200 rounded-lg p-4 flex items-center">
            <CheckCircle className="h-5 w-5 text-green-600 mr-3" />
            <span className="text-green-800">{success}</span>
          </div>
        )}

        {/* Upload Tab */}
        {activeTab === 'upload' && (
          <div className="space-y-6">
            {/* Requirements Card */}
            <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
              <h2 className="text-lg font-semibold text-slate-900 mb-4 flex items-center">
                <FileText className="h-5 w-5 mr-2 text-blue-600" />
                Data Requirements
              </h2>
              <div className="grid md:grid-cols-3 gap-4">
                <div className="bg-blue-50 p-4 rounded-lg">
                  <Calendar className="h-6 w-6 text-blue-600 mb-2" />
                  <h3 className="font-medium text-slate-900">Date</h3>
                  <p className="text-sm text-slate-600">Format: mm/dd/yy or mm/dd/yyyy</p>
                </div>
                <div className="bg-green-50 p-4 rounded-lg">
                  <Target className="h-6 w-6 text-green-600 mb-2" />
                  <h3 className="font-medium text-slate-900">Company Name</h3>
                  <p className="text-sm text-slate-600">Text field with company identifier</p>
                </div>
                <div className="bg-purple-50 p-4 rounded-lg">
                  <DollarSign className="h-6 w-6 text-purple-600 mb-2" />
                  <h3 className="font-medium text-slate-900">Profit</h3>
                  <p className="text-sm text-slate-600">Numerical value (positive or negative)</p>
                </div>
              </div>
            </div>

            {/* Upload Area */}
            <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-8">
              <div className="text-center">
                <div
                  className="border-2 border-dashed border-slate-300 rounded-lg p-12 hover:border-blue-400 transition-colors cursor-pointer"
                  onClick={() => fileInputRef.current?.click()}
                >
                  <Upload className="h-12 w-12 text-slate-400 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-slate-900 mb-2">Upload Excel File</h3>
                  <p className="text-slate-500 mb-4">Click to browse or drag and drop your .xlsx file</p>
                  <div className="bg-slate-50 rounded-lg p-3 inline-block">
                    <span className="text-sm text-slate-600">Supported formats: .xlsx, .xls</span>
                  </div>
                </div>
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".xlsx,.xls"
                  onChange={handleFileUpload}
                  className="hidden"
                />
              </div>

              {file && (
                <div className="mt-6 bg-slate-50 rounded-lg p-4 flex items-center justify-between">
                  <div className="flex items-center">
                    <FileText className="h-5 w-5 text-slate-600 mr-3" />
                    <span className="text-slate-900 font-medium">{file.name}</span>
                    <span className="text-slate-500 ml-2">({(file.size / 1024).toFixed(1)} KB)</span>
                  </div>
                  <button
                    onClick={processData}
                    disabled={loading || !plotlyReady}
                    className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center"
                  >
                    {loading ? (
                      <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent mr-2"></div>
                    ) : (
                      <Activity className="h-4 w-4 mr-2" />
                    )}
                    {loading ? 'Processing...' : 'Analyze with AI'}
                  </button>
                </div>
              )}
            </div>

            {/* Features */}
            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-4">
                <div className="bg-blue-100 p-2 rounded-lg w-fit mb-3">
                  <TrendingUp className="h-5 w-5 text-blue-600" />
                </div>
                <h3 className="font-medium text-slate-900">AI Trend Analysis</h3>
                <p className="text-sm text-slate-600">TensorFlow.js deep learning models</p>
              </div>
              <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-4">
                <div className="bg-green-100 p-2 rounded-lg w-fit mb-3">
                  <Target className="h-5 w-5 text-green-600" />
                </div>
                <h3 className="font-medium text-slate-900">ML Predictions</h3>
                <p className="text-sm text-slate-600">Neural network profit forecasts</p>
              </div>
              <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-4">
                <div className="bg-purple-100 p-2 rounded-lg w-fit mb-3">
                  <BarChart3 className="h-5 w-5 text-purple-600" />
                </div>
                <h3 className="font-medium text-slate-900">Smart Analytics</h3>
                <p className="text-sm text-slate-600">Advanced statistical insights</p>
              </div>
              <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-4">
                <div className="bg-orange-100 p-2 rounded-lg w-fit mb-3">
                  <Download className="h-5 w-5 text-orange-600" />
                </div>
                <h3 className="font-medium text-slate-900">Export Results</h3>
                <p className="text-sm text-slate-600">Download predictions and reports</p>
              </div>
            </div>
          </div>
        )}

        {/* Analysis Tab */}
        {activeTab === 'analysis' && data.length > 0 && (
          <div className="space-y-6">
            {/* Stats Cards */}
            {stats && (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-slate-600">Total Profit</p>
                      <p className="text-2xl font-bold text-slate-900">{formatCurrency(stats.totalProfit)}</p>
                    </div>
                    <div className="bg-blue-100 p-3 rounded-full">
                      <DollarSign className="h-6 w-6 text-blue-600" />
                    </div>
                  </div>
                </div>
                <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-slate-600">Average Profit</p>
                      <p className="text-2xl font-bold text-slate-900">{formatCurrency(stats.avgProfit)}</p>
                    </div>
                    <div className="bg-green-100 p-3 rounded-full">
                      <Target className="h-6 w-6 text-green-600" />
                    </div>
                  </div>
                </div>
                <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-slate-600">Growth Rate</p>
                      <p className={`text-2xl font-bold ${stats.growthRate >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                        {formatPercentage(stats.growthRate)}
                      </p>
                    </div>
                    <div className={`p-3 rounded-full ${stats.growthRate >= 0 ? 'bg-green-100' : 'bg-red-100'}`}>
                      <TrendingUp className={`h-6 w-6 ${stats.growthRate >= 0 ? 'text-green-600' : 'text-red-600'}`} />
                    </div>
                  </div>
                </div>
                <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-slate-600">Data Points</p>
                      <p className="text-2xl font-bold text-slate-900">{stats.dataPoints}</p>
                    </div>
                    <div className="bg-purple-100 p-3 rounded-full">
                      <BarChart3 className="h-6 w-6 text-purple-600" />
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Chart */}
            <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
              <h3 className="text-lg font-semibold text-slate-900 mb-4">AI-Powered Profit Predictions</h3>
              <div className="relative" style={{ minHeight: '400px' }}>
                <div ref={plotRef} style={{ width: '100%', height: '400px' }}></div>
              </div>
              <div className="mt-4 flex items-center justify-center space-x-6">
                <div className="flex items-center">
                  <div className="w-3 h-3 bg-blue-500 rounded-full mr-2"></div>
                  <span className="text-sm text-slate-600">Historical Data</span>
                </div>
                <div className="flex items-center">
                  <div className="w-3 h-3 bg-blue-300 rounded-full mr-2"></div>
                  <span className="text-sm text-slate-600">AI Predictions</span>
                </div>
              </div>
            </div>

            {/* Company-wise Predictions Summary */}
            {predictions.length > 0 && (
              <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
                <h3 className="text-lg font-semibold text-slate-900 mb-4">AI Profit Predictions by Company</h3>
                <div className="grid gap-6">
                  {companies.map((company, index) => {
                    const companyPredictions = predictions.filter(pred => pred.company === company);
                    const totalPredicted = companyPredictions.reduce((sum, pred) => sum + pred.profit, 0);
                    const avgPredicted = totalPredicted / companyPredictions.length;

                    return (
                      <div key={company} className="border border-slate-200 rounded-lg p-4">
                        <div className="flex items-center justify-between mb-3">
                          <h4 className="font-semibold text-slate-900 flex items-center">
                            <div
                              className="w-4 h-4 rounded-full mr-3"
                              style={{ backgroundColor: colors[index % colors.length] }}
                            ></div>
                            {company}
                          </h4>
                          <div className="text-right">
                            <p className="text-sm text-slate-600">6-Month AI Forecast</p>
                            <p className="font-bold text-slate-900">{formatCurrency(totalPredicted)}</p>
                          </div>
                        </div>

                        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
                          {companyPredictions.map((pred, predIndex) => (
                            <div key={predIndex} className="bg-slate-50 rounded-md p-3 text-center">
                              <p className="text-xs text-slate-600 mb-1">{pred.month}</p>
                              <p className="font-medium text-slate-900 text-sm">{formatCurrency(pred.profit)}</p>
                            </div>
                          ))}
                        </div>

                        <div className="mt-3 pt-3 border-t border-slate-200 flex justify-between items-center">
                          <span className="text-sm text-slate-600">Average Monthly Prediction:</span>
                          <span className="font-medium text-slate-900">{formatCurrency(avgPredicted)}</span>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default CompanyProfitPredictor;