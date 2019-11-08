let fs = require('fs')

let base64_decoder = (image, index, path) => {
    fs.writeFile(`${path}/out${index}.png`, image, 'base64', function (err) {
        if (err)
            console.log(err);
        else
            console.log(`/saved_image/out${index}.png saved!`)
    });
}

let remove_all_file = (path) => {
    fs.readdir(path, (err, files) => {
        if (err) throw err;

        for (const file of files) {
            fs.unlink(path + file, err => {
                if (err) throw err;
            });
        }
    });
}

module.exports.base64_decoder = base64_decoder;
module.exports.remove_all_file = remove_all_file;