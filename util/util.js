let fs = require('fs')

let base64_decoder = async (image, index, path) => {
    fs.writeFileSync(`${path}/out${index}.png`, image, 'base64');
    console.log(`save png!`)
}

let remove_all_file = (path) => {
    fs.readdir(path, (err, files) => {
        if (err) throw err;

        for (const file of files) {
            fs.unlinkSync(path + file);
            console.log(`remove png!`)
        }
    });
}

module.exports.base64_decoder = base64_decoder;
module.exports.remove_all_file = remove_all_file;