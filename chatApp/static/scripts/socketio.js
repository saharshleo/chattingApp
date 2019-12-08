document.addEventListener('DOMContentLoaded', () => {
    // Connecting
    var socket = io.connect('http://' + document.domain + ':' + location.port);
    var username = document.querySelector(".username").innerHTML;

    // THIS IS REQUIRED FOR UPDATING SID IN BACKEND
    // socket.on('connect', () => {
    //     socket.emit('connect', `${username}~ is connected`);
    // });


    // Get list of public chat rooms
    publicRooms = [];
    document.querySelectorAll('room-opt').forEach(li => {
        publicRooms.push(li.innerHTML);
    })
    


    // Display received message
    socket.on('message', (msg) => {
        console.log(`Message received: ${msg}`);
        msg = JSON.parse(msg);
        if(msg['room'] !== roomName) {
            console.log("I don't know what to do");
        }
        if(msg['sender'] === 'SYSTEM') {
            let msgDisplay = document.createElement('p');
            msgDisplay.innerHTML = msg['content'];
            let listItem = document.createElement('li');
            listItem.appendChild(msgDisplay);
            document.getElementById('messages-list').appendChild(listItem);
        }
        else if(msg['room'] === roomName) {
            let msgDisplay = document.createElement('p');
            msgDisplay.innerText = `${msg["sender"]} (${msg["timestamp"]}): ${msg["content"]}`;
            let listItem = document.createElement('li');
            listItem.appendChild(msgDisplay);
            document.getElementById('messages-list').appendChild(listItem);
        }
    });

    // Select user input field and send button from DOM
    let sendButton = document.querySelector('#send-btn');
    let userInput = document.querySelector('#user-input');

    // Function to send a message
    sendMessage = () => {
        if(userInput.value !== '') {
            msg = {
                'sender':username,
                'content':userInput.value,
                'room':roomName
            };
            if(publicRooms.includes(roomName)) {
                msg['receiver'] = null;
            }
            else if(roomName === 'GLOBAL') {
                msg['receiver'] = null;
            }
            else {
                msg['receiver'] = document.querySelector('#room-name');
            }
            socket.send(JSON.stringify(msg));
            userInput.value="";
        }
    };

    // Listener for send action: Enter key
    userInput.addEventListener("keyup", (e) => {
        if(e.keyCode === 13) {
            if(userInput === document.activeElement) {
                e.preventDefault();
                sendMessage();
            }
        }
    });

    // Listener for send action: Send button clicked
    sendButton.onclick = () => {
        sendMessage();
    };

    
    // Listener for room-opt clicks
	document.querySelectorAll('.room-opt').forEach(li => {
		
	    li.onclick = () => {
			
	        let newRoom = li.innerHTML;
	        if(newRoom === roomName) {  // User already in that room
	            console.log(`User already in ${roomName}`); // Write alert code later
	        }
	        else {
	            leaveRoom(roomName);
	            joinRoom(newRoom);
                roomName = newRoom;
                document.querySelector('#room-name').innerHTML = newRoom;
	        }
	    }
	});

	// Function for leaving a room
	leaveRoom = (oldRoom) => {
		leave_msg = {
			'sender':username,
			'room':oldRoom
		}
		socket.emit('leave', JSON.stringify(leave_msg));
		document.querySelector('#messages-list').innerHTML = '';
	}

	// Function for joining a roow
	joinRoom = (newRoom) => {
		join_msg = {
			'sender':username,
			'room':newRoom
		}
		socket.emit('join', JSON.stringify(join_msg));
	}



    /* document.querySelectorAll('.user-list-item').forEach(li => {
        li.onclick = () => {

            request = {
                'sender':username,
                'to':li.innerHTML
            };
            socket.emit('request_for_connection', JSON.stringify(request));
        }
    })

    socket.on('request_to_connect', (request) => {
        console.log(`Request to connect: ${request}`);
        request = JSON.parse(request);

        // FOR SOME REASON, THE CODE BELOW IS NEVER REACHED

        // Alert user that he has been requested. Add an onclick for accepting
        // For now, accept all incoming requests
        console.log(`in 'request_to_connect' request was parsed`);
        accept_request(request['sender']);
        
    })

    accept_request = (requester_username) => {
        console.log("accept_request() called");
        newRoom = `${requester_username}ROOMW${username}`;
        accept_msg = {
            'sender':username,
            'requester':requester_username,
            'room':newRoom
        };
        socket.emit('accept_request', JSON.stringify(accept_msg));
        // Redirect to chat screen, or add chatroom somewhere
        // Edit: the newRoom in this case can be requester.sid
        // Edit 2: Not today
        
        leaveRoom(roomName);
        joinRoom(newRoom);
        console.log(`Joining room ${newRoom}`);
    }

    socket.on('request_accepted', (accepted_msg) => {
        console.log(`Request was accepted, Details:\n${accepted_msg}`)
        // Use accepted_msg to join newly created two-person chatroom
    }) */

    document.querySelectorAll('.user-list-item').forEach(li => {
        li.onclick = () => {
            newRoom = `${username}_${li.innerHTML}`;
            msg = {
                'sender':username,
                'receiver':li.innerHTML,
                'room':newRoom
            };
            socket.emit('make_new_room', newRoom);
            leaveRoom(roomName);
            joinRoom(newRoom);
            console.log(`Joining room ${newRoom}`);
        }
        roomName = newRoom;
        document.querySelector('#room-name').innerHTML = li.innerHTML;
    })

    socket.on('load_history', (msgHistory) => {
        msgHistory = JSON.parse(msgHistory);
        for(msgKey in msgHistory) {
            if(msgKey === '0') {
                continue;
            }
            else if(msgKey === '1') {
                if(roomName === msgHistory[msgKey]['room']) {
                    // Correct case, continue
                }
                else {
                    // Incorrect
                    console.log('History received was not of current room')
                    break;
                }
            }
            let msgDisplay = document.createElement('p');
            msgDisplay.innerHTML = msgHistory[msgKey]['content'];
            let listItem = document.createElement('li');
            listItem.appendChild(msgDisplay);
            document.getElementById('messages-list').appendChild(listItem);
        }
    });

});