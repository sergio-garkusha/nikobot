fs = require("fs");

let data = fs.readFileSync('./handfiles.json',
  { encoding: 'utf8', flag: 'r' });

data = JSON.parse(data);

function dates_normalizer() {
  // to this "Date": "2022-08-22T20:24:44+00:00"
  return data.map((item, idx) => {
    item.Num = idx + 1;

    dt = new Date(item["Date"]);

    y = dt.getFullYear();
    m = ('0' + (dt.getMonth() + 1)).slice(-2);
    d = ('0' + dt.getDate()).slice(-2)

    hr = ('0' + dt.getHours()).slice(-2)
    min = ('0' + dt.getMinutes()).slice(-2)
    sec = "00"

    fmtD = `${y}-${m}-${d}T${hr}:${min}:${sec}+00:00`;

    item.Date = fmtD;

    return item;
  });
}

function pib_normalizer() {
  return data.map((item, idx) => {
    if (item.PIB.length === 1) {
      item.PIB = item.PIB[0].split(' ');
    }
    return item;
  });
}

function cats_normalizer() {
  return data.map((item, idx) => {

    return item;
  });
}

dates_normalizer();
pib_normalizer();

fs.writeFileSync('./_handfiles.json', JSON.stringify(data), { encoding: 'utf8' });

console.log(data);
