document.addEventListener('DOMContentLoaded', function() {
    const teamsData = JSON.parse(document.getElementById('teams-data').textContent);
    const teams = {};
    for (const team of teamsData) {
        teams[team.name] = team;
    }

    const teamSelects = document.querySelectorAll('select[name^="team_"]');
    teamSelects.forEach((select, index) => {
        const teamIndex = index + 1;
        select.addEventListener('change', (event) => {
            const teamName = event.target.value;
            const quizzerSelects = document.querySelectorAll(`.quizzer-select[name^="quizzer_${teamIndex}_"]`);

            fetch(`/get_quizzers/${teamName}`)
                .then(response => response.json())
                .then(quizzers => {
                    quizzerSelects.forEach(quizzerSelect => {
                        quizzerSelect.innerHTML = '<option value=""></option>';
                        quizzers.forEach(quizzer => {
                            const option = document.createElement('option');
                            option.value = quizzer.name;
                            option.textContent = quizzer.name;
                            quizzerSelect.appendChild(option);
                        });
                    });
                })
                .catch(error => console.error('Error:', error));
            updateTeamScore(teamIndex);
        });
    });

    function updateTeamScore(teamIndex) {
        const teamScoreEl = document.getElementById(`team_score_${teamIndex}`);
        let score = 0;

        const onTimeCheckbox = document.querySelector(`input[name="on_time_${teamIndex}"]`);
        if (onTimeCheckbox.checked) {
            score += 20;
        }

        const scoreSelects = document.querySelectorAll(`select[name^="score_${teamIndex}_"]`);
        let correctQuizzers = new Set();
        let personalErrors = {};
        let teamErrors = 0;
        let fouls = 0;

        scoreSelects.forEach(scoreSelect => {
            const quizzerSelect = scoreSelect.parentElement.previousElementSibling.querySelector('.quizzer-select');
            const quizzerName = quizzerSelect.value;

            if (scoreSelect.value === 'C') {
                score += 20;
                if (quizzerName) {
                    correctQuizzers.add(quizzerName);
                }
            } else if (scoreSelect.value === 'E') {
                teamErrors++;
                if (quizzerName) {
                    if (!personalErrors[quizzerName]) {
                        personalErrors[quizzerName] = 0;
                    }
                    personalErrors[quizzerName]++;
                    if (personalErrors[quizzerName] > 1) {
                        score -= 10;
                    }
                }
                if (teamErrors > 2) {
                    score -= 10;
                }
            } else if (scoreSelect.value === 'B') {
                const questionNumberString = scoreSelect.name.split('_')[3];
                const questionNumber = parseInt(questionNumberString);
                if (questionNumber <= 16) {
                    score += 20;
                } else {
                    score += 10;
                }
            } else if (scoreSelect.value === 'F') {
                fouls++;
                if (fouls > 2) {
                    score -= 10;
                }
            }
        });

        if (correctQuizzers.size >= 3) {
            score += 10;
        }
        if (correctQuizzers.size >= 4) {
            score += 10;
        }
        if (correctQuizzers.size >= 5) {
            score += 10;
        }

        teamScoreEl.textContent = score;

        let runningTotal = 0;
        const onTimeCheckbox = document.querySelector(`input[name="on_time_${teamIndex}"]`);
        if (onTimeCheckbox.checked) {
            runningTotal = 20;
        }

        for (let i = 1; i <= 26; i++) {
            const scoreSelectsInQuestion = document.querySelectorAll(`select[name^="score_${teamIndex}_"][name$="_${i}"], select[name^="score_${teamIndex}_"][name$="_${i}b"]`);
            scoreSelectsInQuestion.forEach(scoreSelect => {
                if (scoreSelect.value === 'C') {
                    runningTotal += 20;
                } else if (scoreSelect.value === 'E') {
                    // This logic needs to be improved to handle team and personal errors correctly
                    runningTotal -= 10;
                } else if (scoreSelect.value === 'B') {
                    const questionNumberString = scoreSelect.name.split('_')[3];
                    const questionNumber = parseInt(questionNumberString);
                    if (questionNumber <= 16) {
                        runningTotal += 20;
                    } else {
                        runningTotal += 10;
                    }
                } else if (scoreSelect.value === 'F') {
                    // This logic needs to be improved to handle fouls correctly
                    runningTotal -= 10;
                }
            });
            const runningTotalEl = document.getElementById(`running_total_${teamIndex}_${i}`);
            if(runningTotalEl) {
                runningTotalEl.textContent = runningTotal;
            }
        }
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
