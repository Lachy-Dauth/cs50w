document.addEventListener('DOMContentLoaded', () => {
    const bet_btns = document.querySelectorAll('.buy-option');
    const floating_section = document.querySelector('#floating-section');
    const selected_option_name = document.querySelector('#selected-option-name');
    const selected_option_price = document.querySelector('#selected-option-price');
    const ticket_quantity = document.querySelector('#ticket-quantity');
    const total_price = document.querySelector('#total-price');
    const option_id_holder = document.querySelector('#option-id-input');

    let data = {};

    bet_btns.forEach(btn => {
        btn.addEventListener('click', (event) => {
            floating_section.classList.remove('hidden');
            option_id_holder.value = event.target.dataset.optionId;
            fetch_info(event.target.dataset.betId, event.target.dataset.optionId);
        });
    });

    ticket_quantity.addEventListener('input', async function() {
        if (data.reserve !== undefined) {
            const total = await get_successive_price(
                parseInt(data.reserve),
                data.total_tickets,
                data.option_tickets,
                parseInt(ticket_quantity.value)
            );
            total_price.textContent = total;
        }
    });

    async function fetch_info(bet_id, option_id) {
        const response = await fetch(`/api/bet-option/?bet_id=${bet_id}&option_id=${option_id}`);
        data = await response.json();

        selected_option_name.textContent = data.option_name;
        selected_option_price.textContent = await get_price(
            parseFloat(data.reserve),
            data.total_tickets,
            data.option_tickets
        );
        total_price.textContent = await get_successive_price(
            parseFloat(data.reserve),
            data.total_tickets,
            data.option_tickets,
            parseInt(ticket_quantity.value)
        );
    };

    async function get_price(reserve, total_tickets, option_tickets) {
        const url = new URL('/api/price/', window.location.origin);
        const params = {
            reserve: reserve,
            total_tickets: total_tickets,
            option_tickets: option_tickets,
            number: 0
        };
        Object.keys(params).forEach(key => url.searchParams.append(key, params[key]));

        try {
            const response = await fetch(url);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            return data.price;
        } catch (error) {
            console.error('Error fetching price:', error);
        }
    }

    async function get_successive_price(reserve, total_tickets, option_tickets, number) {
        const url = new URL('/api/price/', window.location.origin);
        const params = {
            reserve: reserve,
            total_tickets: total_tickets,
            option_tickets: option_tickets,
            number: number
        };
        Object.keys(params).forEach(key => url.searchParams.append(key, params[key]));

        try {
            const response = await fetch(url);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            return data.successive_price;
        } catch (error) {
            console.error('Error fetching successive price:', error);
        }
    }
});
