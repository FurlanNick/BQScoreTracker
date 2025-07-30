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

    const form = document.querySelector('form');
    form.addEventListener('change', () => {
        const formData = new FormData(form);
        fetch(`/edit_quiz/{{ quiz_name }}`, {
            method: 'POST',
            body: formData
        });
    });

    function updateTeamScore(teamIndex) {
        const teamScoreEl = document.getElementById(`team_score_${teamIndex}`);
        let score = 0;

        const onTimeCheckbox = document.querySelector(`input[name="on_time_${teamIndex}"]`);
        if (onTimeCheckbox.checked) {
            score += 20;
        }

        let runningTotal = 0;
        if (onTimeCheckbox.checked) {
            runningTotal = 20;
        }

        for (let i = 1; i <= 26; i++) {
            const scoreSelectsInQuestion = document.querySelectorAll(`select[name^="score_${teamIndex}_"][name$="_${i}"], select[name^="score_${teamIndex}_"][name$="_${i}b"]`);
            let questionScore = 0;
            let correctQuizzersThisQuestion = new Set();

            scoreSelectsInQuestion.forEach(scoreSelect => {
                const quizzerSelect = scoreSelect.parentElement.previousElementSibling.querySelector('.quizzer-select');
                const quizzerName = quizzerSelect.value;

                if (scoreSelect.value === 'C') {
                    questionScore += 20;
                    if(quizzerName) correctQuizzersThisQuestion.add(quizzerName);
                } else if (scoreSelect.value === 'E') {
                    // This logic needs to be improved to handle team and personal errors correctly
                    questionScore -= 10;
                } else if (scoreSelect.value === 'B') {
                    const questionNumberString = scoreSelect.name.split('_')[3];
                    const questionNumber = parseInt(questionNumberString);
                    if (questionNumber <= 16) {
                        questionScore += 20;
                    } else {
                        questionScore += 10;
                    }
                } else if (scoreSelect.value === 'F') {
                    // This logic needs to be improved to handle fouls correctly
                    questionScore -= 10;
                }
            });

            if(correctQuizzersThisQuestion.size >= 3) questionScore += 10;
            if(correctQuizzersThisQuestion.size >= 4) questionScore += 10;
            if(correctQuizzersThisQuestion.size >= 5) questionScore += 10;

            runningTotal += questionScore;

            const runningTotalEl = document.getElementById(`running_total_${teamIndex}_${i}`);
            if(runningTotalEl) {
                runningTotalEl.textContent = runningTotal;
            }
        }
        teamScoreEl.textContent = runningTotal;
    }

    const onTimeCheckboxes = document.querySelectorAll('input[name^="on_time_"]');
    onTimeCheckboxes.forEach((checkbox, index) => {
        const teamIndex = index + 1;
        checkbox.addEventListener('change', () => {
            updateTeamScore(teamIndex);
        });
    });

    const scoreSelects = document.querySelectorAll('select[name^="score_"]');
    scoreSelects.forEach(select => {
        const teamIndex = select.name.split('_')[1];
        select.addEventListener('change', () => {
            updateTeamScore(teamIndex);
        });
    });
});
