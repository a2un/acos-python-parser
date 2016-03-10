var fs = require('fs');
var python = require('python-shell');
var pythonParser = function() {};

pythonParser.register = function(handlers, app, config) {

  handlers.tools['python-parser'] = pythonParser;

  app.get('/python-parser', function(req, res) {
    res.set('Content-Type', 'text/html');
    fs.readFile(__dirname + '/form.html', function(err, data) {
      if (!err) {
        res.send(data);
      } else {
        res.send("Error");
      }
    });
  });

  app.post('/python-parser', function(req, res) {
    var code = { 'code': req.body.code, 'mode': req.body.mode || 'simple' };
    var options = {
      mode: 'json',
      pythonPath: config.pythonPath || '/usr/bin/python3',
      pythonOptions: ['-u'], // -u is unbuffered output
      scriptPath: __dirname
    };

    var pyshell = new python('parser.py', options);
    pyshell.send(code);

    var response = '';

    pyshell.on('message', function(message) {
      response = message;
    });

    pyshell.end(function(err) {
      if (err) {
        res.json({ status: 'ERROR', message: 'Parsing failed.' });
      } else {
        res.json(response);
      }
    });
  });

};

pythonParser.namespace = 'python-parser';
pythonParser.packageType = 'tool';

pythonParser.meta = {
  'name': 'python-parser',
  'shortDescription': 'Parser for parsing arbitrary Python code to export all language concepts used in the code.',
  'description': '',
  'author': 'Teemu Sirkiä',
  'license': 'MIT',
  'version': '0.0.1',
  'url': ''
};

module.exports = pythonParser;
