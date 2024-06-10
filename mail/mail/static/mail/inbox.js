document.addEventListener('DOMContentLoaded', function() {

    // Use buttons to toggle between views
    document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
    document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
    document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
    document.querySelector('#compose').addEventListener('click', compose_email);

    // By default, load the inbox
    load_mailbox('inbox');

    document.querySelector('form').onsubmit = () => {
        recipients = document.querySelector('#compose-recipients').value;
        subject = document.querySelector('#compose-subject').value;
        body = document.querySelector('#compose-body').value;

        fetch("/emails", {
            method : "post",
            body : JSON.stringify({
                recipients : recipients,
                subject : subject,
                body : body,
            })
        })
        .then(response => response.json())
        .then(result => {
            if (result.error === undefined) {
                document.querySelector('#compose-recipients').value = "";
                document.querySelector('#compose-subject').value = "";
                document.querySelector('#compose-body').value = "";
                load_mailbox('sent')
            }
            else {
                document.querySelector('.error-message').style.display = "block";
                document.querySelector('.error-message').innerHTML = result.error;
            }
        });

        return false;
    };
});

function compose_email() {

    // Show compose view and hide other views
    document.querySelector('#emails-view').style.display = 'none';
    document.querySelector('#email-view').style.display = 'none';
    document.querySelector('#compose-view').style.display = 'block';
    document.querySelector('.error-message').style.display = "none";

    // Clear out composition fields
    document.querySelector('#compose-recipients').value = '';
    document.querySelector('#compose-subject').value = '';
    document.querySelector('#compose-body').value = '';
}

function load_mailbox(mailbox) {
    
    document.querySelector('.error-message').style.display = "none";
    const email_sec = document.querySelector('#emails-view');

    // Show the mailbox and hide other views
    email_sec.style.display = 'block';
    document.querySelector('#email-view').style.display = 'none';
    document.querySelector('#compose-view').style.display = 'none';

    fetch(`/emails/${mailbox}`)
    .then(response => response.json())
    .then(result => {
        result.forEach(email => {
            let email_div = document.createElement("div");
            email_div.classList.add("email-div");
            email_div.onclick = () => load_mail(email.id);
            email_div.innerHTML = `
            <div class="email-sender">From: ${email.sender}</div>
            <div class="email-recip">To: ${email.recipients[0]}${email.recipients.length > 1 ? ", and " + (email.recipients.length - 1) + " others" : ""}</div>
            <div class="email-subject">${email.subject}</div>
            <div class="email-time">${email.timestamp}</div>`;

            if (mailbox !== "sent") {
                let arc_btn = document.createElement("button");
                arc_btn.classList = "btn btn-outline-primary"
                arc_btn.innerHTML = (email.archived == true ? "Unarchive" : "Archive");
                arc_btn.onclick = (event) => {
                    event.stopPropagation();
                    toggle(email.id)
                    arc_btn.innerHTML = (arc_btn.innerHTML === "Archive" ? "Unarchive" : "Archive");
                }
                email_div.appendChild(arc_btn);
            }
            if (!email.read) {
                email_div.classList.add("unread");
            }
            email_sec.appendChild(email_div);
        });
    })

    // Show the mailbox name
    document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;
}

function load_mail(id) {

    document.querySelector('.error-message').style.display = "none";
    document.querySelector('#emails-view').style.display = 'none';
    document.querySelector('#email-view').style.display = 'block';
    document.querySelector('#compose-view').style.display = 'none';
    
    fetch(`/emails/${id}`)
    .then(response => response.json())
    .then(result => {
        document.getElementById('main-email-sender').innerText = result.sender;
        document.getElementById('main-email-recips').innerText = result.recipients.join(", ");
        document.getElementById('main-email-subject').innerText = result.subject;
        document.getElementById('main-email-time').innerText = result.timestamp;
        document.getElementById('main-email-text').innerText = result.body;

        document.querySelector('#reply').onclick = () => {
            compose_email();

            document.querySelector('#compose-recipients').value = result.sender;
            document.querySelector('#compose-subject').value = `Re: ${result.subject}`;
            document.querySelector('#compose-body').value = `On ${result.timestamp} ${result.sender} wrote: \n${result.body}`;
        }

        document.querySelector('#toggle-archive').innerHTML = (result.archived == true ? "Unarchive" : "Archive");
        document.querySelector('#toggle-archive').onclick = () => {
            toggle(result.id)
            let previous = document.querySelector('#toggle-archive').innerHTML;
            document.querySelector('#toggle-archive').innerHTML = (previous === "Archive" ? "Unarchive" : "Archive");
        }
    })

    fetch(`/emails/${id}`, {
        method : "PUT",
        body: JSON.stringify({
            read: true,
        })
    })
}

function toggle(id){
    fetch(`/emails/${id}`)
    .then(response => response.json())
    .then(result => {
        fetch(`/emails/${id}`, {
            method : "PUT",
            body: JSON.stringify({
                archived: !result.archived,
            })
        })
    })
}