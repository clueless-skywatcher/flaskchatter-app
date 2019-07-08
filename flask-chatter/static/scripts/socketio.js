// SocketIO logic for client
document.addEventListener('DOMContentLoaded', () => {
    // The default room is 'Gossip'.
    var socket = io.connect('http://' + document.domain + ':' + location.port)
    let room = 'Gossip';
    joinRoom(room)

    // When the client leaves the current room, emit a 'leave' event to the server
    function leaveRoom(room){
        socket.emit('leave', {
            'username' : username,
            'room' : room
        })
    }

    // When the user joins a room, emit a 'join' event to the server
    function joinRoom(room){
        socket.emit('join', {
            'username' : username,
            'room' : room
        })
        document.querySelector('#display-message').innerHTML = ""
        document.querySelector('#user-message').focus()
    }

    // Function for printing system messages
    function printMsg(msg){
        const p = document.createElement('p')
        p.innerHTML = msg
        document.querySelector('#display-message').append(p)
    }

    // If the server sends a message to the client, trigger the 'message' event
    // Render the incoming message in proper format and display it to the user
    socket.on('message', (data) => {
        const p = document.createElement('p')
        // If the sender of the message is the user itself, use one layout
        // Otherwise use a different layout
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
        
        // If the message is not empty and has a valid username
        // Render the username and message together and append it to the display-message
        // element
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

    // Logic for selecting rooms, if the user joins a different room, log out
    // from the current room and log in to the new room. If the user attempts to
    // join the room he/she is currently in, show a system message
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

    // If the message send button is clicked (or Enter key is pressed)
    // send the data typed in the message input to the server
    document.querySelector("#send-message").onclick = () => {
        socket.send({
            'msg' : document.querySelector("#user-message").value,
            'username' : username,
            'room' : room
        })
        document.querySelector("#user-message").value = ""
    }
})