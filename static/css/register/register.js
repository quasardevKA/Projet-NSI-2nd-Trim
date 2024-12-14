const uname = document.getElementById('username');
const pass = document.getElementById('password');
const email = document.getElementById('email');
const first_name = document.getElementById('first_name');
const last_name = document.getElementById('last_name');
const passconfirm = document.getElementById('password-confirm');
const btnContainer = document.querySelector('.btn-container');
const btn = document.getElementById('btn');
const form = document.querySelector('form');
const msg = document.querySelector('.msg');
btn.disabled = true;

function shiftButton() {
    showMsg();
    const positions = ['shift-left', 'shift-top', 'shift-right', 'shift-bottom'];
    const currentPosition = positions.find(dir => btn.classList.contains(dir));
    const nextPosition = positions[(positions.indexOf(currentPosition) + 1) % positions.length];
    btn.classList.remove(currentPosition);
    btn.classList.add(nextPosition);
}

function showMsg() {
    const isEmpty = uname.value === '' || pass.value === '' || email.value === '' || first_name.value === '' || last_name.value === '' || passconfirm.value === '';
    btn.classList.toggle('no-shift', !isEmpty);

    if (isEmpty) {
        btn.disabled = true
        msg.style.color = 'rgb(218 49 49)';
        msg.innerText = 'Merci de remplir les champs avant de s\'inscrire';
    } else {
        msg.innerText = 'Super ! Maitenant vous pouvez vous inscrire !';
        msg.style.color = '#92ff92';
        btn.disabled = false;
        btn.classList.add('no-shift')
    }
}

btnContainer.addEventListener('mouseover', shiftButton);
btn.addEventListener('mouseover', shiftButton);
form.addEventListener('input',showMsg)
btn.addEventListener('touchstart', shiftButton);
