let emitter = () => {
    return emitterImpl;
}

let emitterImpl = (io, socket) => {
    let room = 'room1'

    return {
        emit(payload){
            console.log(`${payload.device} call [${payload.event}]`);
            
            if(payload.broadcastType === "WITHOUT_SENDER")
                socket.broadcast.to(room).emit(payload.event, {buffer: payload.data, event: payload.event});
            else if(payload.broadcastType === "ALL_CLIENT")
                io.sockets.in(room).emit(payload.event, {buffer: payload.data, event: payload.event});
            else
                io.sockets.in(room).emit(payload.event, {buffer: payload.data, event: payload.event});
        }
    }
}

//deprecated
// let androidEmitter = (io) => {
//     let currentRoom = io.sockets.in('room1');

//     return {
//         emit(event, data){
//             currentRoom.emit(event, {buffer: data})
//         }
//     }
// }

// let windowsEmitter = (io) => {
//     let currentRoom = io.sockets.in('room1');

//     return {
//         emit(event, data){
//             currentRoom.emit(event, {buffer: data})
//         }
//     }
// }

module.exports = emitter;
