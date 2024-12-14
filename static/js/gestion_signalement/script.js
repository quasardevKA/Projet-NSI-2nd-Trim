function banUser(user_id, ban_id) {
    fetch('/ban-user', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ user_id: user_id, ban_id: ban_id })
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
    })
    .catch(error => {
        console.error('Erreur:', error);
    });
}


function delReport(user_id, ban_id) {
    fetch('/del-Report', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ user_id: reportedUserId, ban_id: ban_id })
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
    })
    .catch(error => {
        console.error('Erreur:', error);
    });
}



var reportedUserId = 'reported_user_id_valeur';
var userId = 'user_id_valeur';

document.getElementById('banButton').onclick = function() {
    banUser(reportedUserId, userId);
};

document.getElementById('refuseButton').onclick = function() {
    // Ajoutez votre logique pour le bouton "Refuse"
};

function banUser(reportedUserId, userId) {
    console.log(`Banning user: reportedUserId=${reportedUserId}, userId=${userId}`);
// Ajoutez votre logique de bannissement ici
}

