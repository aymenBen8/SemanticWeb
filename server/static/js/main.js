// Fonction pour gérer la recherche
function searchEntity() {
    const query = document.getElementById('searchInput').value;
    if (query) {
        window.location.href = `/search?query=${encodeURIComponent(query)}`;
    } else {
        alert("Please enter a search term!");
    }
}

// Fonction pour initialiser le carrousel
function initCarousel() {
    let currentSlide = 0;
    const slides = document.querySelectorAll('.carousel-item');
    const totalSlides = slides.length;

    function showSlide(index) {
        const slideWidth = slides[0].clientWidth;
        document.querySelector('.carousel-slide').style.transform = `translateX(${-index * slideWidth}px)`;
    }

    function nextSlide() {
        currentSlide = (currentSlide + 1) % totalSlides;
        showSlide(currentSlide);
    }

    function prevSlide() {
        currentSlide = (currentSlide - 1 + totalSlides) % totalSlides;
        showSlide(currentSlide);
    }

    // Boutons de navigation du carrousel
    document.querySelector('.carousel-button.next').addEventListener('click', nextSlide);
    document.querySelector('.carousel-button.prev').addEventListener('click', prevSlide);

    // Rotation automatique du carrousel
    setInterval(nextSlide, 5000);
}

// Fonction pour gérer les clics sur les cartes
function handleCardClicks() {
    const cards = document.querySelectorAll('.card');
    cards.forEach(card => {
        card.addEventListener('click', () => {
            const entityName = card.querySelector('h3').innerText;
            const entityType = card.parentElement.parentElement.querySelector('h2').innerText.toLowerCase();
            window.location.href = `/${entityType}/${encodeURIComponent(entityName)}`;
        });
    });
}

// Fonction pour gérer les clics sur les résultats de recherche
function handleSearchResultClicks() {
    const searchResults = document.querySelectorAll('.search-result');
    searchResults.forEach(result => {
        result.addEventListener('click', () => {
            const entityName = result.querySelector('h3').innerText;
            const entityType = result.dataset.type;
            window.location.href = `/${entityType}/${encodeURIComponent(entityName)}`;
        });
    });
}

// Fonction pour charger des données via AJAX
function loadData(url, callback) {
    const xhr = new XMLHttpRequest();
    xhr.open('GET', url, true);
    xhr.onload = function () {
        if (xhr.status === 200) {
            callback(JSON.parse(xhr.responseText));
        } else {
            console.error('Erreur lors du chargement des données');
        }
    };
    xhr.send();
}

// Fonction pour afficher les données chargées
function displayData(data, containerId) {
    const container = document.getElementById(containerId);
    if (container) {
        container.innerHTML = '';
        data.forEach(item => {
            const card = document.createElement('div');
            card.className = 'card animated';
            card.innerHTML = `
                <img src="${item.image}" alt="${item.name}">
                <h3>${item.name}</h3>
                <p>${item.description}</p>
            `;
            container.appendChild(card);
        });
    }
}

// Fonction pour initialiser les événements
function initEvents() {
    // Barre de recherche
    document.querySelector('.search-bar button').addEventListener('click', searchEntity);
    document.getElementById('searchInput').addEventListener('keypress', function (e) {
        if (e.key === 'Enter') {
            searchEntity();
        }
    });

    // Cartes
    handleCardClicks();

    // Résultats de recherche
    handleSearchResultClicks();
}

// Fonction pour initialiser l'application
function initApp() {
    initCarousel();
    initEvents();

    // Charger des données supplémentaires via AJAX (exemple)
    loadData('/api/featured-pokemon', function (data) {
        displayData(data, 'featured-pokemon-container');
    });

    loadData('/api/featured-trainers', function (data) {
        displayData(data, 'featured-trainers-container');
    });

    loadData('/api/featured-abilities', function (data) {
        displayData(data, 'featured-abilities-container');
    });

    loadData('/api/featured-locations', function (data) {
        displayData(data, 'featured-locations-container');
    });

    loadData('/api/featured-items', function (data) {
        displayData(data, 'featured-items-container');
    });

    loadData('/api/featured-moves', function (data) {
        displayData(data, 'featured-moves-container');
    });
}

// Initialiser l'application lorsque le DOM est chargé
document.addEventListener('DOMContentLoaded', initApp);

// Fonction pour gérer les erreurs
function handleError(error) {
    console.error('Erreur:', error);
    alert('Une erreur s\'est produite. Veuillez réessayer.');
}

// Fonction pour afficher un message de chargement
function showLoadingMessage() {
    const loadingMessage = document.createElement('div');
    loadingMessage.id = 'loading-message';
    loadingMessage.innerText = 'Chargement en cours...';
    document.body.appendChild(loadingMessage);
}

// Fonction pour masquer le message de chargement
function hideLoadingMessage() {
    const loadingMessage = document.getElementById('loading-message');
    if (loadingMessage) {
        loadingMessage.remove();
    }
}

// Fonction pour gérer les clics sur les boutons de pagination
function handlePaginationClicks() {
    const paginationButtons = document.querySelectorAll('.pagination-button');
    paginationButtons.forEach(button => {
        button.addEventListener('click', function () {
            const page = this.dataset.page;
            loadData(`/api/data?page=${page}`, function (data) {
                displayData(data, 'data-container');
            });
        });
    });
}

// Fonction pour initialiser la pagination
function initPagination() {
    handlePaginationClicks();
}

// Fonction pour gérer les clics sur les filtres
function handleFilterClicks() {
    const filters = document.querySelectorAll('.filter');
    filters.forEach(filter => {
        filter.addEventListener('click', function () {
            const filterValue = this.dataset.filter;
            loadData(`/api/data?filter=${filterValue}`, function (data) {
                displayData(data, 'data-container');
            });
        });
    });
}

// Fonction pour initialiser les filtres
function initFilters() {
    handleFilterClicks();
}

// Fonction pour gérer les clics sur les onglets
function handleTabClicks() {
    const tabs = document.querySelectorAll('.tab');
    tabs.forEach(tab => {
        tab.addEventListener('click', function () {
            const tabId = this.dataset.tab;
            document.querySelectorAll('.tab-content').forEach(content => {
                content.style.display = 'none';
            });
            document.getElementById(tabId).style.display = 'block';
        });
    });
}

// Fonction pour initialiser les onglets
function initTabs() {
    handleTabClicks();
}

// Fonction pour gérer les clics sur les modales
function handleModalClicks() {
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        modal.addEventListener('click', function () {
            this.style.display = 'none';
        });
    });

    const modalTriggers = document.querySelectorAll('.modal-trigger');
    modalTriggers.forEach(trigger => {
        trigger.addEventListener('click', function () {
            const modalId = this.dataset.modal;
            document.getElementById(modalId).style.display = 'block';
        });
    });
}

// Fonction pour initialiser les modales
function initModals() {
    handleModalClicks();
}

// Fonction pour gérer les clics sur les notifications
function handleNotificationClicks() {
    const notifications = document.querySelectorAll('.notification');
    notifications.forEach(notification => {
        notification.addEventListener('click', function () {
            this.remove();
        });
    });
}

// Fonction pour initialiser les notifications
function initNotifications() {
    handleNotificationClicks();
}

// Fonction pour gérer les clics sur les menus déroulants
function handleDropdownClicks() {
    const dropdowns = document.querySelectorAll('.dropdown');
    dropdowns.forEach(dropdown => {
        dropdown.addEventListener('click', function () {
            this.classList.toggle('active');
        });
    });
}

// Fonction pour initialiser les menus déroulants
function initDropdowns() {
    handleDropdownClicks();
}

// Fonction pour gérer les clics sur les boutons de tri
function handleSortClicks() {
    const sortButtons = document.querySelectorAll('.sort-button');
    sortButtons.forEach(button => {
        button.addEventListener('click', function () {
            const sortBy = this.dataset.sort;
            loadData(`/api/data?sort=${sortBy}`, function (data) {
                displayData(data, 'data-container');
            });
        });
    });
}

// Fonction pour initialiser les boutons de tri
function initSortButtons() {
    handleSortClicks();
}

// Fonction pour gérer les clics sur les boutons de filtre avancé
function handleAdvancedFilterClicks() {
    const advancedFilters = document.querySelectorAll('.advanced-filter');
    advancedFilters.forEach(filter => {
        filter.addEventListener('click', function () {
            const filterValue = this.dataset.filter;
            loadData(`/api/data?advanced_filter=${filterValue}`, function (data) {
                displayData(data, 'data-container');
            });
        });
    });
}

// Fonction pour initialiser les filtres avancés
function initAdvancedFilters() {
    handleAdvancedFilterClicks();
}

// Fonction pour gérer les clics sur les boutons de recherche avancée
function handleAdvancedSearchClicks() {
    const advancedSearchButtons = document.querySelectorAll('.advanced-search-button');
    advancedSearchButtons.forEach(button => {
        button.addEventListener('click', function () {
            const searchQuery = document.getElementById('advanced-search-input').value;
            loadData(`/api/data?advanced_search=${searchQuery}`, function (data) {
                displayData(data, 'data-container');
            });
        });
    });
}

// Fonction pour initialiser la recherche avancée
function initAdvancedSearch() {
    handleAdvancedSearchClicks();
}

// Fonction pour gérer les clics sur les boutons de sauvegarde
function handleSaveClicks() {
    const saveButtons = document.querySelectorAll('.save-button');
    saveButtons.forEach(button => {
        button.addEventListener('click', function () {
            const dataId = this.dataset.id;
            saveData(dataId);
        });
    });
}

// Fonction pour initialiser les boutons de sauvegarde
function initSaveButtons() {
    handleSaveClicks();
}

// Fonction pour sauvegarder des données
function saveData(dataId) {
    fetch(`/api/save/${dataId}`, {
        method: 'POST',
    })
    .then(response => response.json())
    .then(data => {
        alert('Données sauvegardées avec succès!');
    })
    .catch(error => {
        handleError(error);
    });
}

// Fonction pour gérer les clics sur les boutons de partage
function handleShareClicks() {
    const shareButtons = document.querySelectorAll('.share-button');
    shareButtons.forEach(button => {
        button.addEventListener('click', function () {
            const dataId = this.dataset.id;
            shareData(dataId);
        });
    });
}

// Fonction pour initialiser les boutons de partage
function initShareButtons() {
    handleShareClicks();
}

// Fonction pour partager des données
function shareData(dataId) {
    fetch(`/api/share/${dataId}`, {
        method: 'POST',
    })
    .then(response => response.json())
    .then(data => {
        alert('Données partagées avec succès!');
    })
    .catch(error => {
        handleError(error);
    });
}

// Fonction pour gérer les clics sur les boutons de téléchargement
function handleDownloadClicks() {
    const downloadButtons = document.querySelectorAll('.download-button');
    downloadButtons.forEach(button => {
        button.addEventListener('click', function () {
            const dataId = this.dataset.id;
            downloadData(dataId);
        });
    });
}

// Fonction pour initialiser les boutons de téléchargement
function initDownloadButtons() {
    handleDownloadClicks();
}

// Fonction pour télécharger des données
function downloadData(dataId) {
    fetch(`/api/download/${dataId}`, {
        method: 'GET',
    })
    .then(response => response.blob())
    .then(blob => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `data-${dataId}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
    })
    .catch(error => {
        handleError(error);
    });
}

// Fonction pour gérer les clics sur les boutons de suppression
function handleDeleteClicks() {
    const deleteButtons = document.querySelectorAll('.delete-button');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function () {
            const dataId = this.dataset.id;
            deleteData(dataId);
        });
    });
}

// Fonction pour initialiser les boutons de suppression
function initDeleteButtons() {
    handleDeleteClicks();
}

// Fonction pour supprimer des données
function deleteData(dataId) {
    fetch(`/api/delete/${dataId}`, {
        method: 'DELETE',
    })
    .then(response => response.json())
    .then(data => {
        alert('Données supprimées avec succès!');
    })
    .catch(error => {
        handleError(error);
    });
}

// Fonction pour gérer les clics sur les boutons de mise à jour
function handleUpdateClicks() {
    const updateButtons = document.querySelectorAll('.update-button');
    updateButtons.forEach(button => {
        button.addEventListener('click', function () {
            const dataId = this.dataset.id;
            updateData(dataId);
        });
    });
}

// Fonction pour initialiser les boutons de mise à jour
function initUpdateButtons() {
    handleUpdateClicks();
}

// Fonction pour mettre à jour des données
function updateData(dataId) {
    fetch(`/api/update/${dataId}`, {
        method: 'PUT',
    })
    .then(response => response.json())
    .then(data => {
        alert('Données mises à jour avec succès!');
    })
    .catch(error => {
        handleError(error);
    });
}

// Fonction pour gérer les clics sur les boutons de réinitialisation
function handleResetClicks() {
    const resetButtons = document.querySelectorAll('.reset-button');
    resetButtons.forEach(button => {
        button.addEventListener('click', function () {
            resetData();
        });
    });
}

// Fonction pour initialiser les boutons de réinitialisation
function initResetButtons() {
    handleResetClicks();
}

// Fonction pour réinitialiser des données
function resetData() {
    fetch('/api/reset', {
        method: 'POST',
    })
    .then(response => response.json())
    .then(data => {
        alert('Données réinitialisées avec succès!');
    })
    .catch(error => {
        handleError(error);
    });
}

// Fonction pour gérer les clics sur les boutons de confirmation
function handleConfirmClicks() {
    const confirmButtons = document.querySelectorAll('.confirm-button');
    confirmButtons.forEach(button => {
        button.addEventListener('click', function () {
            const action = this.dataset.action;
            confirmAction(action);
        });
    });
}

// Fonction pour initialiser les boutons de confirmation
function initConfirmButtons() {
    handleConfirmClicks();
}

// Fonction pour confirmer une action
function confirmAction(action) {
    if (confirm(`Êtes-vous sûr de vouloir ${action}?`)) {
        fetch(`/api/${action}`, {
            method: 'POST',
        })
        .then(response => response.json())
        .then(data => {
            alert(`Action "${action}" effectuée avec succès!`);
        })
        .catch(error => {
            handleError(error);
        });
    }
}

// Fonction pour gérer les clics sur les boutons d'annulation
function handleCancelClicks() {
    const cancelButtons = document.querySelectorAll('.cancel-button');
    cancelButtons.forEach(button => {
        button.addEventListener('click', function () {
            cancelAction();
        });
    });
}

// Fonction pour initialiser les boutons d'annulation
function initCancelButtons() {
    handleCancelClicks();
}

// Fonction pour annuler une action
function cancelAction() {
    alert('Action annulée.');
}

// Fonction pour gérer les clics sur les boutons de retour
function handleBackClicks() {
    const backButtons = document.querySelectorAll('.back-button');
    backButtons.forEach(button => {
        button.addEventListener('click', function () {
            window.history.back();
        });
    });
}

// Fonction pour initialiser les boutons de retour
function initBackButtons() {
    handleBackClicks();
}

// Fonction pour gérer les clics sur les boutons de fermeture
function handleCloseClicks() {
    const closeButtons = document.querySelectorAll('.close-button');
    closeButtons.forEach(button => {
        button.addEventListener('click', function () {
            this.parentElement.style.display = 'none';
        });
    });
}

// Fonction pour initialiser les boutons de fermeture
function initCloseButtons() {
    handleCloseClicks();
}

// Fonction pour gérer les clics sur les boutons de plein écran
function handleFullscreenClicks() {
    const fullscreenButtons = document.querySelectorAll('.fullscreen-button');
    fullscreenButtons.forEach(button => {
        button.addEventListener('click', function () {
            toggleFullscreen();
        });
    });
}

// Fonction pour initialiser les boutons de plein écran
function initFullscreenButtons() {
    handleFullscreenClicks();
}

// Fonction pour basculer en mode plein écran
function toggleFullscreen() {
    if (!document.fullscreenElement) {
        document.documentElement.requestFullscreen();
    } else {
        document.exitFullscreen();
    }
}

// Fonction pour gérer les clics sur les boutons de zoom
function handleZoomClicks() {
    const zoomButtons = document.querySelectorAll('.zoom-button');
    zoomButtons.forEach(button => {
        button.addEventListener('click', function () {
            const zoomLevel = this.dataset.zoom;
            zoomContent(zoomLevel);
        });
    });
}

// Fonction pour initialiser les boutons de zoom
function initZoomButtons() {
    handleZoomClicks();
}

// Fonction pour zoomer le contenu
function zoomContent(zoomLevel) {
    document.body.style.zoom = zoomLevel;
}

// Fonction pour gérer les clics sur les boutons de réglage
function handleSettingsClicks() {
    const settingsButtons = document.querySelectorAll('.settings-button');
    settingsButtons.forEach(button => {
        button.addEventListener('click', function () {
            openSettings();
        });
    });
}

// Fonction pour initialiser les boutons de réglage
function initSettingsButtons() {
    handleSettingsClicks();
}

// Fonction pour ouvrir les réglages
function openSettings() {
    alert('Ouvrir les réglages...');
}

// Fonction pour gérer les clics sur les boutons d'aide
function handleHelpClicks() {
    const helpButtons = document.querySelectorAll('.help-button');
    helpButtons.forEach(button => {
        button.addEventListener('click', function () {
            openHelp();
        });
    });
}

// Fonction pour initialiser les boutons d'aide
function initHelpButtons() {
    handleHelpClicks();
}

// Fonction pour ouvrir l'aide
function openHelp() {
    alert('Ouvrir l\'aide...');
}

// Fonction pour gérer les clics sur les boutons de feedback
function handleFeedbackClicks() {
    const feedbackButtons = document.querySelectorAll('.feedback-button');
    feedbackButtons.forEach(button => {
        button.addEventListener('click', function () {
            openFeedback();
        });
    });
}

// Fonction pour initialiser les boutons de feedback
function initFeedbackButtons() {
    handleFeedbackClicks();
}

// Fonction pour ouvrir le feedback
function openFeedback() {
    alert('Ouvrir le feedback...');
}

// Fonction pour gérer les clics sur les boutons de connexion
function handleLoginClicks() {
    const loginButtons = document.querySelectorAll('.login-button');
    loginButtons.forEach(button => {
        button.addEventListener('click', function () {
            openLogin();
        });
    });
}

// Fonction pour initialiser les boutons de connexion
function initLoginButtons() {
    handleLoginClicks();
}

// Fonction pour ouvrir la connexion
function openLogin() {
    alert('Ouvrir la connexion...');
}

// Fonction pour gérer les clics sur les boutons d'inscription
function handleSignupClicks() {
    const signupButtons = document.querySelectorAll('.signup-button');
    signupButtons.forEach(button => {
        button.addEventListener('click', function () {
            openSignup();
        });
    });
}

// Fonction pour initialiser les boutons d'inscription
function initSignupButtons() {
    handleSignupClicks();
}

// Fonction pour ouvrir l'inscription
function openSignup() {
    alert('Ouvrir l\'inscription...');
}

// Fonction pour gérer les clics sur les boutons de déconnexion
function handleLogoutClicks() {
    const logoutButtons = document.querySelectorAll('.logout-button');
    logoutButtons.forEach(button => {
        button.addEventListener('click', function () {
            logout();
        });
    });
}

// Fonction pour initialiser les boutons de déconnexion
function initLogoutButtons() {
    handleLogoutClicks();
}

// Fonction pour déconnecter l'utilisateur
function logout() {
    alert('Déconnexion...');
}

// Fonction pour gérer les clics sur les boutons de profil
function handleProfileClicks() {
    const profileButtons = document.querySelectorAll('.profile-button');
    profileButtons.forEach(button => {
        button.addEventListener('click', function () {
            openProfile();
        });
    });
}

// Fonction pour initialiser les boutons de profil
function initProfileButtons() {
    handleProfileClicks();
}

// Fonction pour ouvrir le profil
function openProfile() {
    alert('Ouvrir le profil...');
}

// Fonction pour gérer les clics sur les boutons de notification
function handleNotificationClicks() {
    const notificationButtons = document.querySelectorAll('.notification-button');
    notificationButtons.forEach(button => {
        button.addEventListener('click', function () {
            openNotifications();
        });
    });
}

// Fonction pour initialiser les boutons de notification
function initNotificationButtons() {
    handleNotificationClicks();
}

// Fonction pour ouvrir les notifications
function openNotifications() {
    alert('Ouvrir les notifications...');
}

// Fonction pour gérer les clics sur les boutons de messagerie
function handleMessagingClicks() {
    const messagingButtons = document.querySelectorAll('.messaging-button');
    messagingButtons.forEach(button => {
        button.addEventListener('click', function () {
            openMessaging();
        });
    });
}

// Fonction pour initialiser les boutons de messagerie
function initMessagingButtons() {
    handleMessagingClicks();
}

// Fonction pour ouvrir la messagerie
function openMessaging() {
    alert('Ouvrir la messagerie...');
}

// Fonction pour gérer les clics sur les boutons de partage social
function handleSocialShareClicks() {
    const socialShareButtons = document.querySelectorAll('.social-share-button');
    socialShareButtons.forEach(button => {
        button.addEventListener('click', function () {
            const platform = this.dataset.platform;
            shareOnSocial(platform);
        });
    });
}

// Fonction pour initialiser les boutons de partage social
function initSocialShareButtons() {
    handleSocialShareClicks();
}

// Fonction pour partager sur les réseaux sociaux
function shareOnSocial(platform) {
    alert(`Partager sur ${platform}...`);
}

// Fonction pour gérer les clics sur les boutons de téléchargement de média
function handleMediaDownloadClicks() {
    const mediaDownloadButtons = document.querySelectorAll('.media-download-button');
    mediaDownloadButtons.forEach(button => {
        button.addEventListener('click', function () {
            const mediaId = this.dataset.mediaId;
            downloadMedia(mediaId);
        });
    });
}

// Fonction pour initialiser les boutons de téléchargement de média
function initMediaDownloadButtons() {
    handleMediaDownloadClicks();
}

// Fonction pour télécharger un média
function downloadMedia(mediaId) {
    alert(`Télécharger le média ${mediaId}...`);
}

// Fonction pour gérer les clics sur les boutons de lecture de média
function handleMediaPlayClicks() {
    const mediaPlayButtons = document.querySelectorAll('.media-play-button');
    mediaPlayButtons.forEach(button => {
        button.addEventListener('click', function () {
            const mediaId = this.dataset.mediaId;
            playMedia(mediaId);
        });
    });
}

// Fonction pour initialiser les boutons de lecture de média
function initMediaPlayButtons() {
    handleMediaPlayClicks();
}

// Fonction pour lire un média
function playMedia(mediaId) {
    alert(`Lire le média ${mediaId}...`);
}

// Fonction pour gérer les clics sur les boutons de pause de média
function handleMediaPauseClicks() {
    const mediaPauseButtons = document.querySelectorAll('.media-pause-button');
    mediaPauseButtons.forEach(button => {
        button.addEventListener('click', function () {
            const mediaId = this.dataset.mediaId;
            pauseMedia(mediaId);
        });
    });
}

// Fonction pour initialiser les boutons de pause de média
function initMediaPauseButtons() {
    handleMediaPauseClicks();
}

// Fonction pour mettre en pause un média
function pauseMedia(mediaId) {
    alert(`Mettre en pause le média ${mediaId}...`);
}

// Fonction pour gérer les clics sur les boutons de volume de média
function handleMediaVolumeClicks() {
    const mediaVolumeButtons = document.querySelectorAll('.media-volume-button');
    mediaVolumeButtons.forEach(button => {
        button.addEventListener('click', function () {
            const volumeLevel = this.dataset.volume;
            setMediaVolume(volumeLevel);
        });
    });
}

// Fonction pour initialiser les boutons de volume de média
function initMediaVolumeButtons() {
    handleMediaVolumeClicks();
}

// Fonction pour régler le volume d'un média
function setMediaVolume(volumeLevel) {
    alert(`Régler le volume à ${volumeLevel}...`);
}

// Fonction pour gérer les clics sur les boutons de plein écran de média
function handleMediaFullscreenClicks() {
    const mediaFullscreenButtons = document.querySelectorAll('.media-fullscreen-button');
    mediaFullscreenButtons.forEach(button => {
        button.addEventListener('click', function () {
            const mediaId = this.dataset.mediaId;
            toggleMediaFullscreen(mediaId);
        });
    });
}

// Fonction pour initialiser les boutons de plein écran de média
function initMediaFullscreenButtons() {
    handleMediaFullscreenClicks();
}

// Fonction pour basculer en mode plein écran pour un média
function toggleMediaFullscreen(mediaId) {
    alert(`Basculer en mode plein écran pour le média ${mediaId}...`);
}

// Fonction pour gérer les clics sur les boutons de réglage de qualité de média
function handleMediaQualityClicks() {
    const mediaQualityButtons = document.querySelectorAll('.media-quality-button');
    mediaQualityButtons.forEach(button => {
        button.addEventListener('click', function () {
            const qualityLevel = this.dataset.quality;
            setMediaQuality(qualityLevel);
        });
    });
}

// Fonction pour initialiser les boutons de réglage de qualité de média
function initMediaQualityButtons() {
    handleMediaQualityClicks();
}

// Fonction pour régler la qualité d'un média
function setMediaQuality(qualityLevel) {
    alert(`Régler la qualité à ${qualityLevel}...`);
}

// Fonction pour gérer les clics sur les boutons de sous-titres de média
function handleMediaSubtitlesClicks() {
    const mediaSubtitlesButtons = document.querySelectorAll('.media-subtitles-button');
    mediaSubtitlesButtons.forEach(button => {
        button.addEventListener('click', function () {
            const subtitlesLanguage = this.dataset.language;
            setMediaSubtitles(subtitlesLanguage);
        });
    });
}

// Fonction pour initialiser les boutons de sous-titres de média
function initMediaSubtitlesButtons() {
    handleMediaSubtitlesClicks();
}

// Fonction pour régler les sous-titres d'un média
function setMediaSubtitles(subtitlesLanguage) {
    alert(`Régler les sous-titres en ${subtitlesLanguage}...`);
}

// Fonction pour gérer les clics sur les boutons de vitesse de lecture de média
function handleMediaPlaybackSpeedClicks() {
    const mediaPlaybackSpeedButtons = document.querySelectorAll('.media-playback-speed-button');
    mediaPlaybackSpeedButtons.forEach(button => {
        button.addEventListener('click', function () {
            const speedLevel = this.dataset.speed;
            setMediaPlaybackSpeed(speedLevel);
        });
    });
}

// Fonction pour initialiser les boutons de vitesse de lecture de média
function initMediaPlaybackSpeedButtons() {
    handleMediaPlaybackSpeedClicks();
}

// Fonction pour régler la vitesse de lecture d'un média
function setMediaPlaybackSpeed(speedLevel) {
    alert(`Régler la vitesse de lecture à ${speedLevel}...`);
}

// Fonction pour gérer les clics sur les boutons de boucle de média
function handleMediaLoopClicks() {
    const mediaLoopButtons = document.querySelectorAll('.media-loop-button');
    mediaLoopButtons.forEach(button => {
        button.addEventListener('click', function () {
            const mediaId = this.dataset.mediaId;
            toggleMediaLoop(mediaId);
        });
    });
}

// Fonction pour initialiser les boutons de boucle de média
function initMediaLoopButtons() {
    handleMediaLoopClicks();
}

// Fonction pour activer/désactiver la boucle d'un média
function toggleMediaLoop(mediaId) {
    alert(`Activer/désactiver la boucle pour le média ${mediaId}...`);
}

// Fonction pour gérer les clics sur les boutons de partage de média
function handleMediaShareClicks() {
    const mediaShareButtons = document.querySelectorAll('.media-share-button');
    mediaShareButtons.forEach(button => {
        button.addEventListener('click', function () {
            const mediaId = this.dataset.mediaId;
            shareMedia(mediaId);
        });
    });
}

// Fonction pour initialiser les boutons de partage de média
function initMediaShareButtons() {
    handleMediaShareClicks();
}

// Fonction pour partager un média
function shareMedia(mediaId) {
    alert(`Partager le média ${mediaId}...`);
}

