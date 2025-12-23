// static/js/main.js
document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const form = document.getElementById('analysisForm');
    const loading = document.getElementById('loading');
    const results = document.getElementById('results');
    
    if (!form) return;
    
    // Form submission
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const urlInput = document.getElementById('instagramUrl').value;
        
        if (!urlInput.trim()) {
            showAlert('Veuillez entrer une URL Instagram', 'warning');
            return;
        }
        
        // Validate Instagram URL/username
        if (!isValidInstagramInput(urlInput)) {
            showAlert('Format invalide. Entrez une URL Instagram ou un nom d\'utilisateur', 'warning');
            return;
        }
        
        // Show loading
        showLoading(true);
        
        try {
            // Send request to backend
            const response = await fetch('/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    instagram_url: urlInput
                })
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.detail || `Erreur ${response.status}`);
            }
            
            // Display results
            displayResults(data);
            
        } catch (error) {
            console.error('Error:', error);
            showAlert(`Erreur: ${error.message}`, 'danger');
        } finally {
            showLoading(false);
        }
    });
});

// Validate Instagram input
function isValidInstagramInput(input) {
    // Accepts: username, @username, instagram.com/username
    const instagramRegex = /^(?:https?:\/\/)?(?:www\.)?instagram\.com\/([A-Za-z0-9._]+)\/?$|^@?([A-Za-z0-9._]+)$/;
    return instagramRegex.test(input);
}

// Show/hide loading
function showLoading(show) {
    const loading = document.getElementById('loading');
    const results = document.getElementById('results');
    
    if (show) {
        loading.classList.add('active');
        results.classList.remove('active');
        document.getElementById('instagramUrl').setAttribute('disabled', 'true');
    } else {
        loading.classList.remove('active');
        results.classList.add('active');
        document.getElementById('instagramUrl').removeAttribute('disabled');
    }
}

// Display alert
function showAlert(message, type = 'info') {
    // Remove existing alerts
    const existingAlert = document.querySelector('.alert-dismissible');
    if (existingAlert) {
        existingAlert.remove();
    }
    
    const alertHtml = `
        <div class="alert alert-${type} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    const form = document.getElementById('analysisForm');
    if (form) {
        form.insertAdjacentHTML('afterend', alertHtml);
    }
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        const alert = document.querySelector('.alert-dismissible');
        if (alert) {
            alert.remove();
        }
    }, 5000);
}

// Display analysis results
function displayResults(data) {
    // Update posts count
    const postsCount = document.getElementById('postsCount');
    if (postsCount) {
        postsCount.textContent = data.posts_analyzed;
    }
    
    // Display radar chart
    const radarChart = document.getElementById('radarChart');
    if (radarChart && data.visualization) {
        radarChart.src = data.visualization;
        radarChart.style.display = 'block';
    }
    
    // Display personality traits
    displayTraits(data.personality_traits);
    
    // Display sample posts
    displayPosts(data.sample_data);
    
    // Display profile info
    if (data.profile_info) {
        displayProfileInfo(data.profile_info);
    }
    
    // Scroll to results
    const results = document.getElementById('results');
    if (results) {
        results.scrollIntoView({ behavior: 'smooth' });
    }
}

// Display personality traits
function displayTraits(traits) {
    const traitsDetails = document.getElementById('traitsDetails');
    if (!traitsDetails) return;
    
    traitsDetails.innerHTML = '';
    
    for (const [trait, score] of Object.entries(traits)) {
        const percentage = Math.round(score * 100);
        const colorClass = getTraitColorClass(percentage);
        
        const traitHtml = `
            <div class="trait-card">
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <strong>${trait}</strong>
                        <div class="text-muted">${getTraitDescription(trait)}</div>
                    </div>
                    <div class="text-end">
                        <span class="badge ${colorClass} fs-6">${percentage}%</span>
                    </div>
                </div>
                <div class="progress">
                    <div class="progress-bar ${colorClass.replace('bg-', '')}" 
                         style="width: ${percentage}%"></div>
                </div>
            </div>
        `;
        
        traitsDetails.innerHTML += traitHtml;
    }
}

// Get color class based on percentage
function getTraitColorClass(percentage) {
    if (percentage >= 80) return 'bg-success';
    if (percentage >= 60) return 'bg-primary';
    if (percentage >= 40) return 'bg-info';
    if (percentage >= 20) return 'bg-warning';
    return 'bg-secondary';
}

// Get trait description
function getTraitDescription(trait) {
    const descriptions = {
        'Openness': 'Créativité, curiosité, imagination',
        'Conscientiousness': 'Organisation, fiabilité, discipline',
        'Extraversion': 'Sociabilité, énergie, assertivité',
        'Agreeableness': 'Altruisme, coopération, empathie',
        'Neuroticism': 'Émotions, anxiété, stabilité'
    };
    return descriptions[trait] || '';
}

// Display Instagram posts
function displayPosts(posts) {
    const postsGrid = document.getElementById('postsGrid');
    if (!postsGrid) return;
    
    postsGrid.innerHTML = '';
    
    if (!posts || posts.length === 0) {
        postsGrid.innerHTML = `
            <div class="col-12 text-center py-4">
                <i class="fas fa-images fa-3x text-muted mb-3"></i>
                <p class="text-muted">Aucun post disponible</p>
            </div>
        `;
        return;
    }
    
    posts.forEach((post, index) => {
        // Utiliser image_url si disponible, sinon image_path
        const imagePath = post.image_url || post.image_path;
        const imageUrl = imagePath ? `/downloads/${imagePath}` : null;
        
        const postHtml = `
            <div class="col-md-6 col-lg-4 mb-4">
                <div class="card post-card h-100">
                    <div class="position-relative">
                        ${imageUrl ? 
                            `<img src="${imageUrl}" class="post-image" alt="Post ${index + 1}" 
                                 onerror="this.onerror=null; this.src='https://via.placeholder.com/300x200?text=Image+Non+Disponible';"
                                 style="cursor: pointer;" onclick="openImageModal('${imageUrl}')">` :
                            `<div class="post-image bg-light d-flex align-items-center justify-content-center">
                                <i class="fas fa-image fa-3x text-muted"></i>
                                <div class="position-absolute bottom-0 end-0 m-2">
                                    <span class="badge bg-dark"><i class="fas fa-video me-1"></i> Vidéo</span>
                                </div>
                            </div>`
                        }
                        ${post.is_video ? 
                            `<div class="position-absolute top-0 end-0 m-2">
                                <span class="badge bg-dark"><i class="fas fa-video me-1"></i> Vidéo</span>
                            </div>` : ''
                        }
                    </div>
                    <div class="card-body d-flex flex-column">
                        <p class="card-text small flex-grow-1">
                            ${post.caption ? truncateText(post.caption, 100) : 'Pas de description'}
                        </p>
                        <div class="d-flex justify-content-between small text-muted mt-2">
                            <span><i class="fas fa-heart text-danger"></i> ${post.likes || 0}</span>
                            <span><i class="fas fa-comment text-primary"></i> ${post.comments_count || 0}</span>
                            <span>${formatDate(post.date)}</span>
                        </div>
                        ${post.hashtags && post.hashtags.length > 0 ? 
                            `<div class="mt-2">
                                ${post.hashtags.slice(0, 3).map(tag => 
                                    `<span class="hashtag">#${tag}</span>`
                                ).join('')}
                                ${post.hashtags.length > 3 ? 
                                    `<span class="text-muted">+${post.hashtags.length - 3} autres</span>` : ''
                                }
                            </div>` : ''
                        }
                        <div class="mt-2">
                            <a href="${post.url}" target="_blank" class="btn btn-sm btn-outline-primary">
                                <i class="fab fa-instagram me-1"></i> Voir sur Instagram
                            </a>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        postsGrid.innerHTML += postHtml;
    });
}

// Ajoutez cette fonction pour ouvrir les images en grand
function openImageModal(imageUrl) {
    const modalHtml = `
        <div class="modal fade" id="imageModal" tabindex="-1">
            <div class="modal-dialog modal-dialog-centered modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Image du post</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body text-center">
                        <img src="${imageUrl}" class="img-fluid" style="max-height: 70vh;">
                    </div>
                    <div class="modal-footer">
                        <a href="${imageUrl}" download class="btn btn-primary">
                            <i class="fas fa-download me-1"></i> Télécharger
                        </a>
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Fermer</button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Supprimer l'ancienne modal si elle existe
    const oldModal = document.getElementById('imageModal');
    if (oldModal) {
        oldModal.remove();
    }
    
    // Ajouter la nouvelle modal
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    
    // Afficher la modal
    const modal = new bootstrap.Modal(document.getElementById('imageModal'));
    modal.show();
}

// Display profile information
function displayProfileInfo(profile) {
    const profileName = document.getElementById('profileName');
    const profilePic = document.getElementById('profilePic');
    const profileInfo = document.getElementById('profileInfo');
    const profileStats = document.getElementById('profileStats');
    
    if (profileName && profile.username) {
        profileName.textContent = profile.full_name || profile.username;
    }
    
    if (profilePic) {
        profilePic.src = profile.profile_pic_url || 'https://via.placeholder.com/100';
        profilePic.alt = profile.username || 'Profile';
    }
    
    if (profileStats) {
        profileStats.innerHTML = `
            <div><strong>${profile.posts_count || 0}</strong> posts</div>
            <div><strong>${profile.followers || 0}</strong> followers</div>
            <div><strong>${profile.following || 0}</strong> following</div>
        `;
    }
    
    if (profileInfo) {
        profileInfo.innerHTML = `
            <p><strong>Bio:</strong> ${profile.biography || 'Non disponible'}</p>
            <div class="row">
                <div class="col-md-6">
                    <p><i class="fas fa-lock${profile.is_private ? '' : '-open'} me-2"></i>
                    ${profile.is_private ? 'Compte privé' : 'Compte public'}</p>
                </div>
                <div class="col-md-6">
                    <p><i class="fas fa-badge-check${profile.is_verified ? ' text-primary' : ' text-muted'} me-2"></i>
                    ${profile.is_verified ? 'Compte vérifié' : 'Non vérifié'}</p>
                </div>
            </div>
        `;
    }
}

// Helper functions
function truncateText(text, maxLength) {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
}

function formatDate(dateString) {
    if (!dateString) return '';
    try {
        const date = new Date(dateString);
        return date.toLocaleDateString('fr-FR', {
            day: 'numeric',
            month: 'short',
            year: 'numeric'
        });
    } catch (e) {
        return dateString;
    }
}

// Reset analysis
function resetAnalysis() {
    const form = document.getElementById('analysisForm');
    const results = document.getElementById('results');
    
    if (form) form.reset();
    if (results) results.classList.remove('active');
    
    window.scrollTo({ top: 0, behavior: 'smooth' });
}