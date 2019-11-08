var express = require('express');
var router = express.Router();
var fs = require('fs');

/* GET home page. */
router.get('/', function (req, res, next) {
  //json pass
  fs.readFile(`${__dirname}/../data/data.json`, 'utf8', function (err, data) {
    res.end(data);
  });
});

module.exports = router;