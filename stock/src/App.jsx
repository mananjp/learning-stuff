import React, { useState, useRef, useCallback, useEffect } from 'react';
import {
  Upload, TrendingUp, BarChart3, Calendar, DollarSign, FileText, AlertCircle, CheckCircle, Download, Zap, Target,
  Activity, User, Mail, Phone, MapPin, Send, Info, Users, Code, Database, Brain, Cpu, Globe, MessageCircle, Home
} from 'lucide-react';

import * as tf from '@tensorflow/tfjs';
import { UserInfoIcons } from '../components/UserInfoIcons.jsx';
const CompanyProfitPredictor = () => {
  const [file, setFile] = useState(null);
  const [data, setData] = useState([]);
  const [predictions, setPredictions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [stats, setStats] = useState(null);
  const [activeTab, setActiveTab] = useState('upload');
  const [currentPage, setCurrentPage] = useState('home');
  const [plotlyReady, setPlotlyReady] = useState(false);


  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const fileInputRef = useRef(null);
  const plotRef = useRef(null);

  // Load external scripts
  useEffect(() => {
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
          await loadScript('https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js');
        }
        if (!window.Plotly) {
          await loadScript('https://cdnjs.cloudflare.com/ajax/libs/plotly.js/2.18.0/plotly.min.js');
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

      const cleanedData = jsonData.map((row, index) => {
        const date = row.date || row.Date || row.DATE;
        const company = row['company name'] || row['Company Name'] || row.company || row.Company;
        const profit = row.profit || row.Profit || row.PROFIT;

        if (!date || !company || profit === undefined) {
          throw new Error(`Missing required data in row ${index + 1}. Please ensure all rows have date, company name, and profit columns.`);
        }

        let parsedDate;
        if (typeof date === 'number') {
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

      cleanedData.sort((a, b) => a.date - b.date);
      const predictions = await generateTensorFlowPredictions(cleanedData);
      const statistics = calculateStatistics(cleanedData);

      setData(cleanedData);
      setPredictions(predictions);
      setStats(statistics);
      setActiveTab('analysis');
      setSuccess('Data processed successfully!');

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

    const companiesData = {};
    data.forEach(item => {
      if (!companiesData[item.company]) {
        companiesData[item.company] = [];
      }
      companiesData[item.company].push(item);
    });

    const allPredictions = [];

    for (const [company, companyData] of Object.entries(companiesData)) {
      if (companyData.length < 2) continue;

      const sortedData = companyData.sort((a, b) => a.date - b.date);

      const xData = sortedData.map((_, index) => index);
      const yData = sortedData.map(item => item.profit);

      const xs = tf.tensor2d(xData.map(x => [x]), [xData.length, 1]);
      const ys = tf.tensor2d(yData.map(y => [y]), [yData.length, 1]);

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

      await model.fit(xs, ys, {
        epochs: 100,
        verbose: 0,
        validationSplit: 0.2
      });

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

        predictionTensor.dispose();
      }

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
        font: { size: 16, color: '#1f2937' }
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
        y: -0.3,
        x: 0.5,
        xanchor: 'center'
      },
      plot_bgcolor: '#f8fafc',
      paper_bgcolor: '#ffffff',
      margin: { l: 60, r: 30, t: 60, b: 120 }
    };

    window.Plotly.newPlot(plotRef.current, traces, layout, {
      responsive: true,
      displayModeBar: true,
      modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d']
    });
  };

  const handleContactSubmit = (e) => {
    e.preventDefault();
    const { name, email, subject, message } = contactForm;

    const mailtoLink = `mailto:dhananiansh01@gmail.com?subject=${encodeURIComponent(subject || 'New Message from ' + name)}&body=${encodeURIComponent(
      `Name: ${name}\nEmail: ${email}\n\n${message}`
    )}`;

    window.location.href = mailtoLink;
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
    <div className="min-h-screen bg-slate-50">
      {/* Header */}
      <div className="bg-white shadow-lg border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-3">
              <div className="bg-gradient-to-r from-blue-600 to-indigo-600 p-2 rounded-lg">
                <TrendingUp className="h-6 w-6 sm:h-8 sm:w-8 text-white" />
              </div>
              <div>
                <h1 className="text-lg sm:text-2xl font-bold text-slate-900">AI Profit Predictor</h1>
                <p className="text-xs sm:text-sm text-slate-500 hidden sm:block">TensorFlow.js Analytics Dashboard</p>
              </div>
            </div>

            {/* Desktop Navigation */}
            <nav className="hidden md:flex items-center space-x-6">
              <button
                onClick={() => setCurrentPage('home')}
                className={`flex items-center px-3 py-2 rounded-md text-sm font-medium transition-colors ${currentPage === 'home' ? 'bg-blue-100 text-blue-700' : 'text-slate-600 hover:text-slate-900'
                  }`}
              >
                <Home className="h-4 w-4 mr-2" />
                Home
              </button>
              <button
                onClick={() => setCurrentPage('about')}
                className={`flex items-center px-3 py-2 rounded-md text-sm font-medium transition-colors ${currentPage === 'about' ? 'bg-blue-100 text-blue-700' : 'text-slate-600 hover:text-slate-900'
                  }`}
              >
                <Info className="h-4 w-4 mr-2" />
                About
              </button>

            </nav>

            {/* Mobile menu button */}
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="md:hidden p-2 rounded-md text-slate-600 hover:text-slate-900"
            >
              <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
          </div>

          {/* Mobile Navigation */}
          {mobileMenuOpen && (
            <div className="md:hidden border-t border-slate-200 py-4">
              <div className="flex flex-col space-y-2">
                <button
                  onClick={() => { setCurrentPage('home'); setMobileMenuOpen(false); }}
                  className={`flex items-center px-3 py-2 rounded-md text-sm font-medium transition-colors ${currentPage === 'home' ? 'bg-blue-100 text-blue-700' : 'text-slate-600 hover:text-slate-900'
                    }`}
                >
                  <Home className="h-4 w-4 mr-2" />
                  Home
                </button>
                <button
                  onClick={() => { setCurrentPage('about'); setMobileMenuOpen(false); }}
                  className={`flex items-center px-3 py-2 rounded-md text-sm font-medium transition-colors ${currentPage === 'about' ? 'bg-blue-100 text-blue-700' : 'text-slate-600 hover:text-slate-900'
                    }`}
                >
                  <Info className="h-4 w-4 mr-2" />
                  About
                </button>

              </div>
            </div>
          )}
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 sm:py-8">
        {/* Home Page */}
        {currentPage === 'home' && (
          <>
            {/* Tab Navigation */}
            <div className="mb-6 sm:mb-8">
              <div className="flex space-x-1 p-2 bg-white rounded-lg shadow-sm border border-slate-200">
                <button
                  onClick={() => setActiveTab('upload')}
                  className={`flex-1 px-3 py-2 rounded-md font-medium transition-all text-sm ${activeTab === 'upload'
                    ? 'bg-blue-600 text-white shadow-sm'
                    : 'text-slate-600 hover:text-white hover:bg-blue-700'
                    }`}
                >
                  <Upload className="h-4 w-4 inline mr-2" />
                  <span className="hidden sm:inline">Upload Data</span>
                  <span className="sm:hidden">Upload</span>
                </button>
                <button
                  onClick={() => setActiveTab('analysis')}
                  className={`flex-1 px-3 py-2 rounded-md font-medium transition-all text-sm ${activeTab === 'analysis'
                    ? 'bg-blue-600 text-white shadow-sm'
                    : 'text-slate-600 hover:text-white hover:bg-blue-600'
                    }`}
                  disabled={data.length === 0}
                >
                  <BarChart3 className="h-4 w-4 inline mr-2" />
                  <span className="hidden sm:inline">Analysis</span>
                  <span className="sm:hidden">Charts</span>
                </button>
              </div>
            </div>

            {/* Alert Messages */}
            {error && (
              <div className="mb-4 sm:mb-6 bg-red-50 border border-red-200 rounded-lg p-4 flex items-start">
                <AlertCircle className="h-5 w-5 text-red-600 mr-3 mt-0.5 flex-shrink-0" />
                <span className="text-red-800 text-sm">{error}</span>
              </div>
            )}

            {success && (
              <div className="mb-4 sm:mb-6 bg-green-50 border border-green-200 rounded-lg p-4 flex items-start">
                <CheckCircle className="h-5 w-5 text-green-600 mr-3 mt-0.5 flex-shrink-0" />
                <span className="text-green-800 text-sm">{success}</span>
              </div>
            )}

            {/* Upload Tab */}
            {activeTab === 'upload' && (
              <div className="space-y-4 sm:space-y-6">
                {/* Requirements Card */}
                <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-4 sm:p-6">
                  <h2 className="text-lg font-semibold text-slate-900 mb-4 flex items-center">
                    <FileText className="h-5 w-5 mr-2 text-blue-600" />
                    Data Requirements
                  </h2>
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
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
                <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-4 sm:p-8">
                  <div className="text-center">
                    <div
                      className="border-2 border-dashed border-slate-300 rounded-lg p-8 sm:p-12 hover:border-blue-400 transition-colors cursor-pointer"
                      onClick={() => fileInputRef.current?.click()}
                    >
                      <Upload className="h-10 w-10 sm:h-12 sm:w-12 text-slate-400 mx-auto mb-4" />
                      <h3 className="text-lg font-medium text-slate-900 mb-2">Upload Excel File</h3>
                      <p className="text-slate-500 mb-4 text-sm sm:text-base">Click to browse or drag and drop your .xlsx file</p>
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
                    <div className="mt-6 bg-slate-50 rounded-lg p-4 flex flex-col sm:flex-row items-start sm:items-center justify-between space-y-3 sm:space-y-0">
                      <div className="flex items-center">
                        <FileText className="h-5 w-5 text-slate-600 mr-3 flex-shrink-0" />
                        <div>
                          <span className="text-slate-900 font-medium text-sm">{file.name}</span>
                          <span className="text-slate-500 ml-2 text-sm">({(file.size / 1024).toFixed(1)} KB)</span>
                        </div>
                      </div>
                      <button
                        onClick={processData}
                        disabled={loading || !plotlyReady}
                        className="w-full sm:w-auto bg-blue-600 text-white px-4 sm:px-6 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center"
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
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
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

                </div>
              </div>
            )}

            {/* Analysis Tab */}
            {activeTab === 'analysis' && data.length > 0 && (
              <div className="space-y-4 sm:space-y-6">
                {/* Stats Cards */}
                {stats && (
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                    <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-4 sm:p-6">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-sm text-slate-600">Total Profit</p>
                          <p className="text-xl sm:text-2xl font-bold text-slate-900">{formatCurrency(stats.totalProfit)}</p>
                        </div>
                        <div className="bg-blue-100 p-3 rounded-full">
                          <DollarSign className="h-5 w-5 sm:h-6 sm:w-6 text-blue-600" />
                        </div>
                      </div>
                    </div>
                    <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-4 sm:p-6">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-sm text-slate-600">Average Profit</p>
                          <p className="text-xl sm:text-2xl font-bold text-slate-900">{formatCurrency(stats.avgProfit)}</p>
                        </div>
                        <div className="bg-green-100 p-3 rounded-full">
                          <Target className="h-5 w-5 sm:h-6 sm:w-6 text-green-600" />
                        </div>
                      </div>
                    </div>
                    <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-4 sm:p-6">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-sm text-slate-600">Growth Rate</p>
                          <p className={`text-xl sm:text-2xl font-bold ${stats.growthRate >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                            {formatPercentage(stats.growthRate)}
                          </p>
                        </div>
                        <div className="bg-purple-100 p-3 rounded-full">
                          <TrendingUp className="h-5 w-5 sm:h-6 sm:w-6 text-purple-600" />
                        </div>
                      </div>
                    </div>
                    <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-4 sm:p-6">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-sm text-slate-600">Data Points</p>
                          <p className="text-xl sm:text-2xl font-bold text-slate-900">{stats.dataPoints}</p>
                        </div>
                        <div className="bg-orange-100 p-3 rounded-full">
                          <BarChart3 className="h-5 w-5 sm:h-6 sm:w-6 text-orange-600" />
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* Chart */}
                <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-4 sm:p-6">
                  <h2 className="text-lg font-semibold text-slate-900 mb-4 flex items-center">
                    <BarChart3 className="h-5 w-5 mr-2 text-blue-600" />
                    Interactive Profit Analysis
                  </h2>
                  <div ref={plotRef} className="w-full h-96"></div>
                  <div className="flex justify-center mt-4">
                    <span className='text-red-500'>DISCLAIMER</span>: The chart generated using Plotly.js is completely based of calculations and predictions,it may get incorrect.
                  </div>
                </div>

                {/* Company Breakdown */}
                <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-4 sm:p-6">
                  <h2 className="text-lg font-semibold text-slate-900 mb-4 flex items-center">
                    <Users className="h-5 w-5 mr-2 text-blue-600" />
                    Company Performance
                  </h2>
                  <div className="space-y-3">
                    {companies.map((company, index) => {
                      const companyData = data.filter(d => d.company === company);
                      const totalProfit = companyData.reduce((sum, d) => sum + d.profit, 0);
                      const avgProfit = totalProfit / companyData.length;
                      const color = colors[index % colors.length];

                      return (
                        <div key={company} className="flex items-center justify-between p-3 bg-slate-50 rounded-lg">
                          <div className="flex items-center space-x-3">
                            <div className="w-3 h-3 rounded-full" style={{ backgroundColor: color }}></div>
                            <div>
                              <p className="font-medium text-slate-900">{company}</p>
                              <p className="text-sm text-slate-600">{companyData.length} data points</p>
                            </div>
                          </div>
                          <div className="text-right">
                            <p className="font-medium text-slate-900">{formatCurrency(totalProfit)}</p>
                            <p className="text-sm text-slate-600">Avg: {formatCurrency(avgProfit)}</p>
                          </div>
                        </div>
                      );
                    })}
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
          </>
        )}

        {/* About Page */}
        {currentPage === 'about' && (
          <div className="space-y-6">
            <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 sm:p-8">
              <h2 className="text-2xl font-bold text-slate-900 mb-6">About AI Profit Predictor</h2>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                <div>
                  <h3 className="text-lg font-semibold text-slate-900 mb-3 flex items-center">
                    <Brain className="h-5 w-5 mr-2 text-blue-600" />
                    Advanced AI Technology
                  </h3>
                  <p className="text-slate-600 mb-4">
                    Our platform leverages TensorFlow.js to run neural networks directly in your browser,
                    providing real-time profit predictions without sending your data to external servers.
                  </p>

                  <h3 className="text-lg font-semibold text-slate-900 mb-3 flex items-center">
                    <Database className="h-5 w-5 mr-2 text-green-600" />
                    Data Processing
                  </h3>
                  <p className="text-slate-600">
                    We support Excel files with automatic data cleaning and validation. Our system can
                    handle multiple companies and time series data with intelligent date parsing.
                  </p>
                </div>

                <div>
                  <h3 className="text-lg font-semibold text-slate-900 mb-3 flex items-center">
                    <Cpu className="h-5 w-5 mr-2 text-purple-600" />
                    Machine Learning Models
                  </h3>
                  <p className="text-slate-600 mb-4">
                    Our neural networks use multiple layers with ReLU activation and Adam optimization
                    to learn complex patterns in your profit data and generate accurate forecasts.
                  </p>

                  <h3 className="text-lg font-semibold text-slate-900 mb-3 flex items-center">
                    <Globe className="h-5 w-5 mr-2 text-orange-600" />
                    Privacy First
                  </h3>
                  <p className="text-slate-600">
                    All processing happens locally in your browser. Your sensitive financial data
                    never leaves your device, ensuring complete privacy and security.
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-gradient-to-r from-blue-600 to-indigo-600 rounded-xl p-6 sm:p-8 text-white">
              <h3 className="text-xl font-bold mb-3">Features & Capabilities</h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                <div className="flex items-center space-x-2">
                  <CheckCircle className="h-5 w-5 text-green-300" />
                  <span>Real-time AI predictions</span>
                </div>
                <div className="flex items-center space-x-2">
                  <CheckCircle className="h-5 w-5 text-green-300" />
                  <span>Interactive visualizations</span>
                </div>
                <div className="flex items-center space-x-2">
                  <CheckCircle className="h-5 w-5 text-green-300" />
                  <span>Statistical analysis</span>
                </div>
                <div className="flex items-center space-x-2">
                  <CheckCircle className="h-5 w-5 text-green-300" />
                  <span>Multi-company support</span>
                </div>
                <div className="flex items-center space-x-2">
                  <CheckCircle className="h-5 w-5 text-green-300" />
                  <span>Trend analysis</span>
                </div>
                <div className="flex items-center space-x-2">
                  <CheckCircle className="h-5 w-5 text-green-300" />
                  <span>Export capabilities</span>
                </div>
              </div>
            </div>
            <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 sm:p-8">
              <h2 className="text-2xl font-bold text-slate-900 mb-6">Information about developers of this project</h2>
              <hr />
              

              <div className="flex pt-3 flex-row sm:flex-row items-start sm:items-center space-y-4 sm:space-y-0 sm:space-x-6">
                <div className="flex pt-7 w-full flex-row justify-between items-start sm:items-center space-x-4">
                  <UserInfoIcons
                avatar="https://avatars.githubusercontent.com/u/187887332?v=4"
                name="Manan Panchal"
                role="Backend developer"
                email="mananpanchal@gmail.com"
                info="Experienced backend developer specializing in TensorFlow.js and machine learning model development. Led multiple AI-driven projects focused on financial forecasting and data analysis."              
                github="https://github.com/mananjp"
                />
                <UserInfoIcons
                avatar="https://avatars.githubusercontent.com/u/189432138?v=4"
                name="Ansh Dhanani"
                role="frontend developer"
                email="dhananiansh01@gmail.com"
                info="frontend developer with expertise in React.js, Tailwind CSS, and UI/UX design. Passionate about creating intuitive and responsive web applications with modern JavaScript frameworks."              
                github="https://github.com/Ansh-dhanani"
                />
                 
                </div>

              </div>

            </div>
          </div>
        )}

      </div>

      {/* Footer */}
      <footer className="bg-white border-t border-slate-200 mt-12">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-0 py-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div>
              <div className="flex items-center space-x-2 mb-4">
                <div className="bg-gradient-to-r from-blue-600 to-indigo-600 p-2 rounded-lg">
                  <TrendingUp className="h-5 w-5 text-white" />
                </div>
                <h3 className="font-bold text-slate-900">AI Profit Predictor</h3>
              </div>
              <p className="text-slate-600 text-sm">
                Advanced machine learning platform for business profit analysis and forecasting.
              </p>
            </div>
            <div>
              <h4 className="font-semibold text-slate-900 mb-3">Features</h4>
              <ul className="space-y-2 text-sm text-slate-600">
                <li>TensorFlow.js Integration</li>
                <li>Real-time Predictions</li>
                <li>Interactive Visualizations</li>
                <li>Statistical Analysis</li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold text-slate-900 mb-3">Technology</h4>
              <ul className="space-y-2 text-sm text-slate-600">
                <li>React & Tailwind CSS</li>
                <li>Neural Networks</li>
                <li>Browser-based ML</li>
                <li>Privacy-first Design</li>
              </ul>
            </div>
          </div>
          <div className="border-t border-slate-200 mt-5 pt-8 text-center">
            <p className="text-sm text-slate-600">
              © 2024 AI Profit Predictor. Built with React, TensorFlow.js, and advanced machine learning.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default CompanyProfitPredictor;