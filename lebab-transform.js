var path = require('path');
var resolve = require('resolve');
var stdin = require('get-stdin');

var opts = JSON.parse(process.argv[2]);

if (!opts.options) opts.options = {};
if (opts.filename) opts.options.filename = opts.filename;

// console.log("Opts")
// console.dir(opts);

(function(done) {

	// if (opts.use_local_babel && opts.filename) {
	//   findBabel(path.dirname(opts.filename), resolveGlobal);
	// } else {
	resolveGlobal();
	// }

	function findLebab(basedir, next) {
		var ropts = {
			basedir: basedir
		};
		resolve('lebab', ropts, function(err, file, pkg) {
			// this calls the function below when done
			if (!err) {
				return done(require(file), {
					file: file,
					pkg: pkg
				});
			}

			next();

		});
	}

	function resolveGlobal() {
		findLebab(opts.node_modules, function() {
			throw new Error('Couldn\'t find lebab');
		});
	}

}(function(lebab, row) {

	// lebab is a Transformer object
	// row contains package.json for lebab
	// console.log("lebab:")
	// console.dir(lebab)
		// console.dir(row)

	// this function gets called when the function at line 12 is finished, by calling done() at line ~24

	var debugLog = '';
	if (opts.debug) {
		debugLog = '\n\n';
		debugLog += '// lebab@' + row.pkg.version + ' (' + row.file + ')\n';
		debugLog += '// filename: ' + opts.filename + '\n';
		// debugLog += '// ' + JSON.stringify(opts) + '\n';
	}

	// console.log("DebugLog");
	// console.log(debugLog);

	stdin().then(function(data) {

		try {
			// console.log("data:")
			// console.log(data)

			var code = "" // babel.transform(data, opts.options).code;
			myLebabTransformer = new lebab.Transformer

			myLebabTransformer.read(data);
			myLebabTransformer.applyTransformations();
			
			code = myLebabTransformer.out();

			if (opts.debug) {
				code += debugLog;
			}
			if (opts.newline_at_eof && code[code.length - 1] !== '\n') {
				code += '\n';
			}

			process.stdout.write(code);
		} catch (err) {
			var message = err.name;
			if (err.codeFrame) { // babel@5.x
				message += [err.message, err.codeFrame].filter(Boolean).join('\n\n');
			} else { // babel@4.x
				message += err.annotated || err.message;
			}
			if (opts.debug) {
				message += debugLog;
			}
			process.stderr.write(message);

		}


	});

}));