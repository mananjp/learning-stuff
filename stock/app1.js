let workbookData = null;

document.getElementById('file-input').addEventListener('change', function(e) {
  const reader = new FileReader();
  reader.onload = function(e) {
    const data = new Uint8Array(e.target.result);
    const workbook = XLSX.read(data, {type: 'array'});
    workbookData = XLSX.utils.sheet_to_json(workbook.Sheets[workbook.SheetNames[0]]);
  };
  reader.readAsArrayBuffer(e.target.files[0]);
});

document.getElementById('analyze-btn').addEventListener('click', async function() {
  if (!workbookData) {
    document.getElementById('result').innerText = "Please upload an XLSX file first.";
    return;
  }
  const companyMap = {};
  workbookData.forEach(row => {
    const name = row['company name'];
    if (!companyMap[name]) companyMap[name] = [];
    companyMap[name].push(row);
  });

  let bestCompany = null, bestPrediction = -Infinity;
  const predictions = {};

  // ML prediction for each company
  for (const name of Object.keys(companyMap)) {
    const entries = companyMap[name]
      .map(r => ({
        x: new Date(r['date']).getTime(),
        y: Number(r['profit'] || 0)
      }))
      .sort((a, b) => a.x - b.x);

    if (entries.length < 2) continue; // we need at least 2 points

    const xs = entries.map((e, i) => i); // using index for x
    const ys = entries.map(e => e.y);

    const xsTensor = tf.tensor1d(xs);
    const ysTensor = tf.tensor1d(ys);

    const model = tf.sequential();
    model.add(tf.layers.dense({units: 1, inputShape: [1]}));
    model.compile({loss: 'meanSquaredError', optimizer: 'sgd'});
    await model.fit(xsTensor, ysTensor, {epochs: 100, verbose: 0});

    const nextX = xs.length;
    const prediction = model.predict(tf.tensor2d([nextX], [1, 1])).dataSync()[0];
    predictions[name] = prediction;

    if (prediction > bestPrediction) {
      bestPrediction = prediction;
      bestCompany = name;
    }
  }

  document.getElementById('result').innerText =
    bestCompany
      ? `Predicted most profitable company: ${bestCompany} (Predicted next profit: ${bestPrediction.toFixed(2)})`
      : 'Could not analyze data. Please check your file format.';

  // Plotly plotting 
 const traces = [];

Object.keys(companyMap).forEach((name, idx) => {
  const entries = companyMap[name]
    .map(r => ({
      date: r['date'],
      profit: Number(r['profit'] || 0)
    }))
    .sort((a, b) => new Date(a.date) - new Date(b.date));

  // Actual profits trace
  traces.push({
    x: entries.map(e => e.date),
    y: entries.map(e => e.profit),
    mode: 'lines+markers',
    name: `${name} (actual)`,
    marker: { size: 6 },
    line: { shape: 'spline' }
  });

  // Predicted profit trace
  const lastDate = new Date(entries[entries.length - 1].date);
  const nextDate = new Date(lastDate.getTime() + 24*60*60*1000);
  traces.push({
    x: [nextDate.toISOString().slice(0, 10)],
    y: [predictions[name]],
    mode: 'markers',
    name: `${name} (predicted)`,
    marker: { size: 14, color: 'red', symbol: 'star' }
  });
});

const layout = {
  title: 'Company Profit Trends and Predictions',
  xaxis: { title: 'Date', type: 'category' }, // Using category for exact label matching
  yaxis: { title: 'Profit' },
  legend: { orientation: 'h' }
};

Plotly.newPlot('profitPlot', traces, layout);

});
