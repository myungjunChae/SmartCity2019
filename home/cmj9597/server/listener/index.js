let fs = require('fs');
let event = require('./event.json');
let util = require('../util/util.js')

let listener = (socket, device) => {
    console.log("Device : ", device);

    if (device !== 'undefined' || device !== null) {
        let emitter = require('../emitter/index')();

        //Attach default Event Listener
        defaultListener(socket, emitter);
    } else {
        //TODO
        //Error Exception
    }
}

let defaultListener = (socket, emitter) => {
    const io = require('../app');
    event = JSON.parse(JSON.stringify(event));

    let device = socket.handshake.query.device;

    let injection = (ele, data, emitter) => {
        let payload = {
            device: device,
            broadcastType: ele.type
        };

        //injection
        if (ele.event == 'EVENT_SEND_IMAGES') {
            payload['event'] = ele.event;
            payload['data'] = data;
        }

        //event emitting
        emitter.emit(payload);
    };

    //attach event
    event.list.general.forEach(ele => {
        console.log("Attach Event : ", ele.event);

        socket.on(ele.event, (data) => {
            //tensorflow
            let image_path = require('path').dirname(require.main.filename) + '/object_detection_tensorflow/saved_image/'
            util.remove_all_file(image_path)

            console.log('length = ', data.length);
            data.forEach((value, index) => {
                util.base64_decoder(value, index, image_path)
            })

            /*for (let temp in data) {
                console.log(data);
            }*/
            //injection(ele, data, emitter(io, socket));
        });
    });
}

let androidListener = (socket, emitter) => {
    const io = require('../app');
    event = JSON.parse(JSON.stringify(event));

    let device = socket.handshake.query.device;

    let injection = (ele, data, emitter) => {
        let payload = {
            device: device,
            broadcastType: ele.type
        };

        if (ele.event == 'EVENT_SEND_TAKED_PHOTO') {
            payload['event'] = ele.event;
            payload['data'] = data.replace(/\n/gi, "");
        }

        emitter.emit(payload);

    };

    event.list.label.android.tablet.forEach(ele => {
        console.log("Attach Event : ", ele.event);

        socket.on(ele.event, (data) => {
            injection(ele, data, emitter(io, socket));
        });
    });

}

let windowsListener = (socket, emitter) => {
    const io = require('../app');
    event = JSON.parse(JSON.stringify(event));

    let device = socket.handshake.query.device;

    let injection = (ele, data, emitter) => {
        let payload = {
            device: device,
            broadcastType: ele.type
        };

        if (ele.event == 'EVENT_SEND_ORIGINAL_IMAGE') {
            payload['event'] = ele.event;
            payload['data'] = data;
        } else if (ele.event == 'EVENT_SEND_INSPECTION_IMAGE') {
            payload['event'] = ele.event;
            payload['data'] = data;
        } else if (ele.event == 'EVENT_SEND_LABEL_EACH_RESULT') {
            payload['event'] = ele.event;
            payload['data'] = data;
        }

        emitter.emit(payload);

    };

    event.list.label.window.forEach(ele => {
        console.log("Attach Event : ", ele.event);

        socket.on(ele.event, (data) => {
            injection(ele, data, emitter(io, socket));
        });
    });
}

module.exports.listener = listener;


//broadcast emit
//socket.broadcast.emit('send', {type: 'image', buffer: 'broad'});
// fs.writeFile(`${__dirname}/image.png`, Buffer.from(data, 'base64'), errFunction())

// listener(socket);
// emitter(socket);

//socket.emit('toclient', { msg: 'Welcome !' });

//socket.emit('receiveImage', { image: true, buffer: data });
/*socket.on('fromclient', function (data) {
    socket.broadcast.emit('toclient', data); // 자신을 제외하고 다른 클라이언트에게 보냄
    socket.emit('toclient', data); // 해당 클라이언트에게만 보냄. 다른 클라이언트에 보낼려면?
    console.log('Message from client :' + data.msg);
})*/