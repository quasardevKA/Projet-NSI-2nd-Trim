var url = window.location.pathname; // Trouver la partie après "/dashboard/" 
var partieApresDashboard = url.split("/dashboard/")[1];
var current_conv_with_user = partieApresDashboard.replace("/", "")
console.log(current_conv_with_user)

document.addEventListener('DOMContentLoaded', function() {
    window.onbeforeunload = null;
    window.onunload = null;
    
    window.addEventListener('load', function() {
        window.print = function() {};
    });

    document.addEventListener('keydown', function(event) {
        if (event.key === 'p' && (event.ctrlKey || event.metaKey)) {
            event.preventDefault();
        }
    });

    // Autres scripts pour le dashboard
});

function NewConvWithUser() {
    var username = document.getElementById('search-member-input').value;

    // Appel Ajax pour obtenir l'UUID du contact
    fetch('/search_user', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username: username })
    })
    .then(response => response.json())
    .then(data => {
        if (data.uuid) {
            // Redirection vers la page de conversation
            window.location.href = `/dashboard/${data.uuid}`;
            console.log(data.uuid);
        } else {
            alert('Utilisateur non trouvé');
        }
    })
    .catch((error) => {
        console.error('Erreur:', error);
    });
}




function searchUsers() {
    var query = document.getElementById('search-input').value;

    fetch(`/search_users?query=${query}`)
        .then(response => response.json())
        .then(data => {
            var resultsContainer = document.getElementById('results');
            resultsContainer.innerHTML = '';

            if (data.length === 0) {
                resultsContainer.textContent = 'Aucun utilisateur avec ce nom d\'utilisateur existe';
                return;
            }

            data.forEach(function(user) {
                var li = document.createElement('li');
                li.className = 'card contact-item';
                li.innerHTML = `
                    <div class="card-body">
                        <div class="d-flex align-items-center">
                            <!-- Avatar -->
                            <div class="avatar me-4">
                                <img src="data:image/png;base64,${user.profile_image}" alt="${user.username}'s profile image" class="avatar-label bg-success text-white" style="border-radius: 50%;">
                            </div>
                            <!-- Avatar -->
                            <!-- Content -->
                            <div class="flex-grow-1 overflow-hidden">
                                <div class="d-flex align-items-center mb-1">
                                    <h5 class="text-truncate mb-0 me-auto">${user.first_name} ${user.last_name}</h5>
                                </div>
                                <div class="d-flex align-items-center">
                                    <div class="text-truncate me-auto">${user.username}</div>
                                </div>
                            </div>
                            <!-- Content -->
                            <!-- Dropdown -->
                            <div class="dropdown">
                                <button class="btn btn-icon btn-base btn-sm" type="button" data-bs-toggle="dropdown" aria-expanded="false">
                                    <i class="ri-more-fill"></i>
                                </button>
                                <ul class="dropdown-menu dropdown-menu-right">
                                    <li>
                                        <a class="dropdown-item d-flex align-items-center justify-content-between" onclick="sendFriendRequest('${user.id}')">Demander en amis<i class="ri-message-2-line"></i></a>
                                    </li>
                                    <li>
                                        <a class="dropdown-item d-flex align-items-center justify-content-between" onclick=" reportUser('${user.id}')">Signaler l'utilisateur<i class="ri-edit-line"></i></a>
                                    </li>
                                    <li>
                                        <div class="dropdown-divider"></div>
                                    </li>
                                    <li>
                                        <a class="dropdown-item d-flex align-items-center justify-content-between" href="#">Bloquer l'utilisateur<i class="ri-forbid-line"></i></a>
                                    </li>
                                </ul>
                            </div>
                            <!-- Dropdown -->
                        </div>
                    </div>
                `;
                resultsContainer.appendChild(li);
            });
        })
        .catch(error => {
            console.error('Erreur:', error);
        });
}

document.addEventListener('DOMContentLoaded', function() {
    fetch('/friend_requests')
        .then(response => response.json())
        .then(data => {
            var requestsContainer = document.getElementById('requestsFriendsRequest');
            requestsContainer.innerHTML = '';
            console.log(data)
            data.forEach(function(request) {
                var div = document.createElement('div');
                div.className = 'card mb-3';
                div.innerHTML = `
                    <div class="card-body">
                        <div class="d-flex align-items-center">
                            <!-- Avatar -->
                            <div class="avatar me-4">
                                <img src="data:image/png;base64,${request.profile_image}" alt="${request.requester_first_name} ${request.requester_last_name}" class="avatar-label bg-soft-success text-success" style="border-radius: 50%; width: 50px; height: 50px;">
                            </div>
                            <!-- Avatar -->
                            <div class="flex-grow-1">
                                <div class="d-flex align-items-center overflow-hidden">
                                    <h5 class="me-auto text-break mb-0">${request.requester_first_name} ${request.requester_last_name}</h5>
                                    <span class="small text-muted text-nowrap ms-2">04:45 PM</span>
                                </div>
                                <div class="d-flex align-items-center">
                                    <div class="line-clamp me-auto">Vous a envoyé une demande d'ami</div>
                                    <div class="dropdown ms-5">
                                        <button class="btn btn-icon btn-base btn-sm" type="button" data-bs-toggle="dropdown" aria-expanded="false">
                                            <i class="ri-more-fill"></i>
                                        </button>
                                        <ul class="dropdown-menu">
                                            <li><a class="dropdown-item" href="#">See less often</a></li>
                                            <li><a class="dropdown-item" href="#">Hide</a></li>
                                        </ul>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="card-footer">
                        <div class="row gx-4">
                            <div class="col">
                                <a href="#" class="btn btn-secondary btn-sm w-100">Refuser</a>
                            </div>
                            <div class="col">
                                <button onclick="acceptFriendRequest('${request.request_id}')" class="btn btn-primary btn-sm w-100">Accepter</button>
                            </div>
                        </div>
                    </div>
                `;
                requestsContainer.appendChild(div);
            });
        })
        .catch(error => {
            console.error('Erreur:', error);
        });
});


function sendFriendRequest(receiverId) {
    fetch('/send_friend_request', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ receiver_id: receiverId })
    })
    .then(response => response.json())
    .then(data => {
        ;   
    })
    .catch(error => {
        console.error('Erreur:', error);
    });
}

document.addEventListener('DOMContentLoaded', function() {
    // Récupérer l'ID de l'utilisateur courant
    fetch('/get_user_id')
    .then(response => response.json())
    .then(data => {
        var socket = io.connect('https://' + document.domain + ':' + location.port);
        var userId = data.user_id;

        socket.on('connect', function() {
            socket.emit('join', { user_id: userId });
        });

        socket.on('receive_message', function(data) {
            if (data.to === userId) {
                addMessageToDOM(data);
            }
        });

        socket.on('connect', function() {
            console.log('Connected to WebSocket');
        });

        socket.on('friend_request', function(data) {
            addFriendRequestToDOM(data);
        });

        socket.on('update_contacts', function(data) {
            var hasContactsElement = document.getElementById('has_contacts');
            if (hasContactsElement) {
                print(hasContactsElement.value)
                hasContactsElement.value = data.has_contacts;
                print(hasContactsElement.value)
                // Optionnel : Mettre à jour d'autres parties de l'interface utilisateur en conséquence
            }
        });
        socket.on('remove_friend_request', function(data){
            console.log(data)
        });

        socket.on('typing', function(data) {
            if (data.from === contactId) {
                document.getElementById('typing-notification').style.display = 'block';
                var element = document.getElementById("autoscroll");
                element.scrollTop = element.scrollHeight;
            }
        });

        socket.on('stop_typing', function(data) {
            if (data.from === contactId) {
                document.getElementById('typing-notification').style.display = 'none';
                var element = document.getElementById("autoscroll");
                element.scrollTop = element.scrollHeight;
            }
        });

        var messageInput = document.getElementById('message_input');
        var typingTimeout;
        var contactId = current_conv_with_user;  // Remplace par l'ID réel du contact

        messageInput.addEventListener('keypress', function(event) {
            if (event.key !== 'Enter') {
                socket.emit('typing', { from: userId, to: contactId });
                console.log("est en train d'écrire")
                clearTimeout(typingTimeout);
                typingTimeout = setTimeout(function() {
                    socket.emit('stop_typing', { from: userId, to: contactId });
                }, 2000);
            }else {
                socket.emit('stop_typing', { from: userId, to: contactId });
            }
        });
        
        messageInput.addEventListener('blur', function() {
            console.log("n'est pas en train d'écrire")
            socket.emit('stop_typing', { from: userId, to: contactId });
        });
    

        // Ajouter le message au DOM
        function addMessageToDOM(message) {
            var conversationsContainer = document.getElementById('conversation_user');
            var senderInfo = message.sender_id === userId ? 'self' : 'other';
            console.log(message.sender_id)
            var div = document.createElement('div');
            div.className = `message ${senderInfo === 'self' ? 'self' : ''}`;
            div.innerHTML = `
                <div class="message-wrap">
                    <div class="message-item">
                        <div class="message-content">
                            <span>${message.message || 'Aucun message'}</span>
                        </div>
                        <div class="dropdown align-self-center">
                            <button class="btn btn-icon btn-base btn-sm" type="button" data-bs-toggle="dropdown" aria-expanded="false">
                                <i class="ri-more-2-fill"></i>
                            </button>
                            <ul class="dropdown-menu ${senderInfo === 'self' ? 'dropdown-menu-end' : ''}">
                                <li>
                                    <a class="dropdown-item d-flex align-items-center justify-content-between" href="#">Edit
                                        <i class="ri-edit-line"></i>
                                    </a>
                                </li>
                                <li>
                                    <a class="dropdown-item d-flex align-items-center justify-content-between" href="#">Share
                                        <i class="ri-share-line"></i>
                                    </a>
                                </li>
                                <li>
                                    <a class="dropdown-item d-flex align-items-center justify-content-between" href="#">Delete
                                        <i class="ri-delete-bin-line"></i>
                                    </a>
                                </li>
                            </ul>
                        </div>
                    </div>
                </div>
            `;
            conversationsContainer.appendChild(div);
            var element = document.getElementById("autoscroll");
            element.scrollTop = element.scrollHeight;
        }

        // Fonction pour envoyer un message
        var messageInput = document.getElementById('message_input');
        messageInput.addEventListener('keypress', function(event) {
            if (event.key === 'Enter') {
                event.preventDefault();
                var message = messageInput.value;

                fetch('/send_message', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        contact_id: contactId,
                        message: message
                    })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        messageInput.value = '';
                        // Ajouter le message au DOM
                        addMessageToDOM({
                            sender_id: userId,
                            message: message,
                            send_time: new Date().toISOString(),
                            profile_image: '', // Vous pouvez ajouter la bonne image ici
                            first_name: '', // Vous pouvez ajouter le bon prénom ici
                            last_name: '' // Vous pouvez ajouter le bon nom ici
                        });
                        // Envoyer le message via WebSocket
                        socket.emit('send_message', {
                            contact_id: contactId,
                            sender_id: userId,
                            message: message,
                            send_time: new Date().toISOString()
                        });
                    } else {
                        console.error('Erreur:', data.error);
                    }
                })
                .catch(error => {
                    console.error('Erreur:', error);
                });
            }
        });

        // Initialiser les messages existants
        fetch(`/get_messages/${contactId}`)
        .then(response => response.json())
        .then(data => {
            data.messages.forEach(message => addMessageToDOM(message));
        })
        .catch(error => {
            console.error('Erreur:', error);
        });
    })
    .catch(error => {
        console.error('Erreur:', error);
    });
    

    function addFriendRequestToDOM(request) {
        var requestsContainer = document.getElementById('requestsFriendsRequest');

        var div = document.createElement('div');
        div.setAttribute('name', request.request_id);
        print(request.request_id)
        div.className = 'card mb-3';
        div.innerHTML = `
            <div class="card-body">
                <div class="d-flex align-items-center">
                    <div class="avatar me-4">
                        <img src="data:image/png;base64,${request.profile_image || ''}" alt="${request.requester_first_name || ''} ${request.requester_last_name || ''}" class="avatar-label bg-soft-success text-success" style="border-radius: 50%; width: 50px; height: 50px;">
                    </div>
                    <div class="flex-grow-1">
                        <div class="d-flex align-items-center overflow-hidden">
                            <h5 class="me-auto text-break mb-0">${request.requester_first_name || 'N/A'} ${request.requester_last_name || 'N/A'}</h5>
                            <span class="small text-muted text-nowrap ms-2">04:45 PM</span>
                        </div>
                        <div class="d-flex align-items-center">
                            <div class="line-clamp me-auto">Vous a envoyé une demande d'ami</div>
                            <div class="dropdown ms-5">
                                <button class="btn btn-icon btn-base btn-sm" type="button" data-bs-toggle="dropdown" aria-expanded="false">
                                    <i class="ri-more-fill"></i>
                                </button>
                                <ul class="dropdown-menu">
                                    <li><a class="dropdown-item" href="#">See less often</a></li>
                                    <li><a class="dropdown-item" href="#">Hide</a></li>
                                </ul>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <div class="card-footer">
                <div class="row gx-4">
                    <div class="col">
                        <a href="#" class="btn btn-secondary btn-sm w-100">Refuser</a>
                    </div>
                    <div class="col">
                        <button onclick="acceptFriendRequest('${request.request_id}')" class="btn btn-primary btn-sm w-100">Accepter</button>
                    </div>
                </div>
            </div>
        `;
        requestsContainer.appendChild(div);
    }

fetch('/friend_requests')
    .then(response => response.json())
    .then(data => {
        var requestsContainer = document.getElementById('requestsFriendsRequest');
        requestsContainer.innerHTML = '';

        if (data.length === 0) {
            requestsContainer.textContent = 'Aucune demande d\'ami reçue.';
            return;
        }
        console.log(data);

        data.forEach(function(request) {
            addFriendRequestToDOM(request);
        });
    })
    .catch(error => {
        console.error('Erreur:', error);
    });
    document.getElementById('typing-notification').style.display = 'none';
});


function reportUser(reportedUserId) {
    const reason = prompt("Pourquoi voulez-vous signaler cet utilisateur ?");
        if (!reason) {
            return;
        }

        fetch('/report_user', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ reported_user_id: reportedUserId, reason: reason })
        })
        .then(response => response.json())
        .then(data => {
            alert(data.message);
        })
        .catch(error => {
            console.error('Erreur:', error);
        });
}

function acceptFriendRequest(requestId) {
    fetch('/accept_friend_request', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ request_id: requestId })
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
        // Retirer la demande d'ami de la liste
    })
    .catch(error => {
        console.error('Erreur:', error);
    });
}

document.addEventListener('DOMContentLoaded', function() {
fetch('/user_contacts')
    .then(response => response.json())
    .then(data => {
        var contactsContainer = document.getElementById('list-contacts');
        contactsContainer.innerHTML = '';

        if (data.length === 0) {
            contactsContainer.textContent = 'Aucun contact trouvé.';
            return;
        }

        data.forEach(function(contact) {
            console.log(contact);
            var li = document.createElement('li');
            li.className = 'card contact-item mb-3';
            console.log(contact.contact_id)
            if (contact.contact_id == current_conv_with_user) {
                li.className += ' active';
                console.log("active pour", current_conv_with_user)
            }

            li.innerHTML = `
                <a href="/dashboard/${contact.contact_id}" class="contact-link"></a>
                <div class="card-body">
                    <div class="d-flex align-items-center">
                        <!-- Avatar -->
                        <div class="avatar avatar-online me-4">
                            <span class="avatar-label bg-soft-primary text-primary">${contact.first_name[0]}${contact.last_name[0]}</span>
                        </div>
                        <!-- Avatar -->

                        <!-- Content -->
                        <div class="flex-grow-1 overflow-hidden">
                            <div class="d-flex align-items-center mb-1">
                                <h5 class="text-truncate mb-0 me-auto">${contact.first_name || 'N/A'} ${contact.last_name || 'N/A'}</h5>
                                <p class="small text-muted text-nowrap ms-4 mb-0">8:12 AM</p>
                            </div>
                            <div class="d-flex align-items-center">
                                <div class="line-clamp me-auto">${contact.last_message || 'Aucun message'}</div>
                                <span class="badge rounded-pill bg-primary ms-2">${contact.unread_messages_count || 0}</span>
                            </div>
                        </div>
                        <!-- Content -->
                    </div>
                </div>
            `;
            contactsContainer.appendChild(li);
        });
    })
    .catch(error => {
        console.error('Erreur:', error);
    });
});

document.addEventListener('DOMContentLoaded', function() {
    var logoutButton = document.getElementById('logout_button');
    console.log("CLICKE")
    logoutButton.addEventListener('click', function() {
        fetch('/logout', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => {
            if (response.redirected) {
                window.location.href = response.url;
            }
        })
        .catch(error => {
            console.error('Erreur:', error);
        });
    });
});