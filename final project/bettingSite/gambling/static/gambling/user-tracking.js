document.addEventListener('DOMContentLoaded', function () {
    let ctx = document.getElementById('profitGraph').getContext('2d');
    let profitData = {
        labels: JSON.parse(document.getElementById('profitData').dataset.labels),
        datasets: [ //{
        //     label: 'Profit',
        //     data: JSON.parse(document.getElementById('profitData').dataset.cumulativeProfit),
        //     borderColor: 'rgba(75, 192, 192, 1)',
        //     borderWidth: 2,
        //     fill: false
        // },
        {
            label: 'Balance + Active Ticket Value',
            data: JSON.parse(document.getElementById('profitData').dataset.currentReserves),
            borderColor: 'rgba(153, 102, 255, 1)',
            borderWidth: 2,
            fill: false
        }]
    };

    let profitGraph = new Chart(ctx, {
        type: 'line',
        data: profitData,
        options: {
            scales: {
                x: {
                    type: 'time',
                    time: {
                        unit: 'day'
                    },
                    adapters: {
                        date: {
                            locale: 'en'
                        }
                    },
                    title: {
                        display: true,
                        text: 'Time'
                    }
                },
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Amount'
                    }
                }
            }
        }
    });
});
