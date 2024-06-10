document.addEventListener('DOMContentLoaded', () => {
    const bet_btns = document.querySelectorAll('.buy-option');
    const floating_section = document.querySelector('#floating-section');
    const selected_option_name = document.querySelector('#selected-option-name');
    const selected_option_price = document.querySelector('#selected-option-price');
    const ticket_quantity = document.querySelector('#ticket-quantity');
    const total_price = document.querySelector('#total-price');
    const option_id_holder = document.querySelector('#option-id-input');

    let data = {};

    bet_btns.forEach(btn => (
        btn.onclick = () => {
            floating_section.classList.remove('hidden');
            option_id_holder.value = event.target.dataset.optionId;
            fetch_info(event.target.dataset.betId, event.target.dataset.optionId);
        }
    ))

    ticket_quantity.addEventListener('input', function() {
        total_price.textContent = round(get_successive_price(parseInt(data.reserve), data.total_tickets, data.option_tickets, parseInt(ticket_quantity.value)))
    });

    async function fetch_info(bet_id, option_id) {
        const response = await fetch(`/api/bet-option/?bet_id=${bet_id}&option_id=${option_id}`);
        data = await response.json();

        selected_option_name.textContent = data.option_name;
        selected_option_price.textContent = round(get_price(parseInt(data.reserve), data.total_tickets, data.option_tickets))
        total_price.textContent = round(get_successive_price(parseInt(data.reserve), data.total_tickets, data.option_tickets, parseInt(ticket_quantity.value)))
    };
})

function get_price(reserve, total_tickets, option_tickets) {
    return Math.max(round(1 - 0.01 * (reserve - option_tickets)), 0)
}

function get_successive_price(reserve, total_tickets, option_tickets, number){
    if (number == 0) {
        return 0
    }
    current_price = round(get_price(reserve, total_tickets, option_tickets))
    return current_price + get_successive_price(reserve + 0.99*current_price, total_tickets + 1, option_tickets + 1, number - 1)
}

function round(num) {
    return Math.ceil(num * 100) / 100
}