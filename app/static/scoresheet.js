document.addEventListener('DOMContentLoaded', function() {
    const teamSelects = document.querySelectorAll('select[name^="team_"]');

    teamSelects.forEach((select, index) => {
        const teamIndex = index + 1;
        select.addEventListener('change', (event) => {
            const teamName = event.target.value;
            const quizzerSelects = document.querySelectorAll(`.quizzer-select[name^="quizzer_${teamIndex}_"]`);

            quizzerSelects.forEach(quizzerSelect => {
                quizzerSelect.innerHTML = '<option value=""></option>';
            });

            if (teamName) {
                fetch(`/get_quizzers/${teamName}`)
                    .then(response => response.json())
                    .then(quizzers => {
                        quizzerSelects.forEach(quizzerSelect => {
                            const selectedQuizzer = quizzerSelect.value;
                            quizzerSelect.innerHTML = '<option value=""></option>';
                            quizzers.forEach(quizzer => {
                                const option = document.createElement('option');
                                option.value = quizzer.name;
                                option.textContent = quizzer.name;
                                quizzerSelect.appendChild(option);
                            });
                            quizzerSelect.value = selectedQuizzer;
                        });

                        quizzerSelects.forEach(select => {
                            select.addEventListener('change', () => {
                                const selectedQuizzers = Array.from(quizzerSelects).map(s => s.value);
                                quizzerSelects.forEach(s => {
                                    Array.from(s.options).forEach(o => {
                                        o.disabled = selectedQuizzers.includes(o.value) && o.value !== s.value;
                                    });
                                });
                            });
                        });
                    })
                    .catch(error => console.error('Error:', error));
            }
        });
    });
});
