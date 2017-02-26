// Tool used to export data to json
const SqliteToJson = require('sqlite-to-json');
const sqlite3 = require('sqlite3');
const exporter = new SqliteToJson({
  client: new sqlite3.Database('./categoryapp.db')
});
exporter.save('item', './data/item.json', function (err) {
  console.log(err);
});
