document.addEventListener('DOMContentLoaded', () => {
    var socket = io.connect('http://' + document.domain + ':' + location.port)
    let room = 'Gossip';
    joinRoom(room)

    function leaveRoom(room){
        socket.emit('leave', {
            'username' : username,
            'room' : room
        })
    }

    function joinRoom(room){
        socket.emit('join', {
            'username' : username,
            'room' : room
        })
        document.querySelector('#display-message').innerHTML = ""
        document.querySelector('#user-message').focus()
    }

    function printMsg(msg){
        const p = document.createElement('p')
        p.innerHTML = msg
        document.querySelector('#display-message').append(p)
    }

    socket.on('message', (data) => {
        const p = document.createElement('p')
        if (data.username == username){
            p.className = 'mymessage-layout'
        }
        else{
            p.className = 'othermessage-layout'
        }
        const span_usn = document.createElement('span')
        span_usn.className = 'username-layout'
        const br = document.createElement('br')
        const span_time = document.createElement('span')
        span_time.className = 'spantime-layout'
        const span_msg = document.createElement('span')
        span_msg.className = 'message-text'

        if (data.username && data.msg){
            span_usn.innerHTML = data.username
            span_time.innerHTML = data.timestamp
            span_msg.innerHTML = data.msg
            p.innerHTML = span_usn.outerHTML + br.outerHTML + span_msg.outerHTML + br.outerHTML + span_time.outerHTML + br.outerHTML
            document.querySelector("#display-message").append(p)
        }
        else {
            printMsg(data.msg)
        }
        
    })

    document.querySelectorAll('.select-room').forEach(p => {
        p.onclick = () => {
            let newroom = p.innerHTML
            if (newroom == room){
                msg = `Cannot rejoin ${room} if already in this room`
                printMsg(msg)
            }
            else{
                leaveRoom(room)
                joinRoom(newroom)
                room = newroom
            }
        }
    })

    document.querySelector("#send-message").onclick = () => {
        socket.send({
            'msg' : document.querySelector("#user-message").value,
            'username' : username,
            'room' : room
        })
        document.querySelector("#user-message").value = ""
    }
})