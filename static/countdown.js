// Définir la date de début et de fin
const countdownStart = new Date("November 15, 2024 00:00:00").getTime();
const countdownEnd = new Date("January 1, 2025 23:59:59").getTime();

// Calculer les intervalles avant le début de la validité
const fiveMonthsBefore = countdownStart - (5 * 30 * 24 * 60 * 60 * 1000);
const fourMonthsBefore = countdownStart - (4 * 30 * 24 * 60 * 60 * 1000);
const threeMonthsBefore = countdownStart - (3 * 30 * 24 * 60 * 60 * 1000);
const twoMonthsBefore = countdownStart - (2 * 30 * 24 * 60 * 60 * 1000);
const oneMonthBefore = countdownStart - (30 * 24 * 60 * 60 * 1000);
const twoWeeksBefore = countdownStart - (14 * 24 * 60 * 60 * 1000);
const oneWeekBefore = countdownStart - (7 * 24 * 60 * 60 * 1000);

// Mettre à jour le compteur toutes les 1 secondes
const x = setInterval(function () {
    // Obtenir la date et l'heure actuelles
    const now = new Date().getTime();
    const countdownMessage = document.getElementById('countdown-message');
    const countdownTimer = document.getElementById('countdown-timer');

    // Affichage avant le début du compte à rebours
    if (now < countdownStart) {
        countdownTimer.style.display = 'none';
        if (now >= fiveMonthsBefore && now < fourMonthsBefore) {
            countdownMessage.innerText = "Cinq mois avant l'ouverture du leasing";
        } else if (now >= fourMonthsBefore && now < threeMonthsBefore) {
            countdownMessage.innerText = "Quatre mois avant l'ouverture du leasing";
        } else if (now >= threeMonthsBefore && now < twoMonthsBefore) {
            countdownMessage.innerText = "Trois mois avant l'ouverture du leasing";
        } else if (now >= twoMonthsBefore && now < oneMonthBefore) {
            countdownMessage.innerText = "Deux mois avant l'ouverture du leasing";
        } else if (now >= oneMonthBefore && now < twoWeeksBefore) {
            countdownMessage.innerText = "Un mois avant l'ouverture du leasing";
        } else if (now >= twoWeeksBefore && now < oneWeekBefore) {
            countdownMessage.innerText = "Deux semaines avant l'ouverture du leasing";
        } else if (now >= oneWeekBefore && now < countdownStart) {
            countdownMessage.innerText = "Une semaine avant l'ouverture du leasing";
        } else {
            countdownMessage.innerText = "";
        }
    }
    // Affichage pendant la validité du compte à rebours
    else if (now >= countdownStart && now <= countdownEnd) {
        countdownTimer.style.display = 'flex';
        countdownMessage.innerText = " Temps restant avant clôture";

        // Calculer la différence entre maintenant et la date de fin
        const distance = countdownEnd - now;

        // Calculer les jours, heures, minutes et secondes
        const days = Math.floor(distance / (1000 * 60 * 60 * 24));
        const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((distance % (1000 * 60)) / 1000);

        // Afficher les résultats dans les éléments HTML
        document.querySelector(".days").innerHTML = days;
        document.querySelector(".hours").innerHTML = hours;
        document.querySelector(".minutes").innerHTML = minutes;
        document.querySelector(".seconds").innerHTML = seconds;
    }
    // Affichage après la fin de la validité du compte à rebours
    else {
        countdownTimer.style.display = 'none';
        countdownMessage.innerHTML = "Le leasing est fermé. Les inscriptions pour le leasing ont pris fin le 1er janvier à minuit. Revenez l'année prochaine pour de nouvelles opportunités.";
    }
}, 1000);
