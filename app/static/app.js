// PDF List - Upload Modal
function showUploadModal() {
    document.getElementById('uploadModal').classList.add('active');
}

function closeUploadModal() {
    document.getElementById('uploadModal').classList.remove('active');
    document.getElementById('uploadForm').reset();
}

async function handleUpload(event) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    
    // Show loading modal
    closeUploadModal();
    console.log('Showing loading modal...');
    showLoading('Uploading PDF...');
    
    try {
        const response = await fetch('/api/pdfs', {
            method: 'POST',
            body: formData
        });
        
        if (response.ok) {
            window.location.reload();
        } else {
            const error = await response.json();
            hideLoading();
            alert(error.detail || 'Upload failed');
        }
    } catch (error) {
        hideLoading();
        alert('Upload failed: ' + error.message);
    }
}

// PDF List - Edit Title Modal
function editPdfTitle(pdfId, currentTitle) {
    document.getElementById('editPdfId').value = pdfId;
    document.getElementById('editTitle').value = currentTitle;
    document.getElementById('editModal').classList.add('active');
}

function closeEditModal() {
    document.getElementById('editModal').classList.remove('active');
    document.getElementById('editForm').reset();
}

async function handleEditTitle(event) {
    event.preventDefault();
    
    const pdfId = document.getElementById('editPdfId').value;
    const formData = new FormData(event.target);
    
    try {
        const response = await fetch(`/api/pdfs/${pdfId}`, {
            method: 'PATCH',
            body: formData
        });
        
        if (response.ok) {
            window.location.reload();
        } else {
            const error = await response.json();
            alert(error.detail || 'Update failed');
        }
    } catch (error) {
        alert('Update failed: ' + error.message);
    }
}

// PDF List - Delete PDF
async function deletePdf(pdfId) {
    if (!confirm('Are you sure you want to delete this PDF?')) {
        return;
    }
    
    showLoading('Deleting PDF...');
    
    try {
        const response = await fetch(`/api/pdfs/${pdfId}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            window.location.reload();
        } else {
            const error = await response.json();
            hideLoading();
            alert(error.detail || 'Delete failed');
        }
    } catch (error) {
        hideLoading();
        alert('Delete failed: ' + error.message);
    }
}

// PDF View - Generate MCQs
async function handleGenerate(event, pdfId) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const requestedCount = formData.get('requested_count');
    
    // Disable button
    const btn = document.getElementById('generateBtn');
    btn.disabled = true;
    btn.textContent = 'Generating...';
    
    try {
        const response = await fetch(`/api/pdfs/${pdfId}/mcq-sets`, {
            method: 'POST',
            body: formData
        });
        
        if (response.ok) {
            const data = await response.json();
            // Start polling for status
            pollGenerationStatus(data.mcq_set.id);
        } else {
            const error = await response.json();
            alert(error.detail || 'Generation failed');
            btn.disabled = false;
            btn.textContent = 'Generate MCQs';
        }
    } catch (error) {
        alert('Generation failed: ' + error.message);
        btn.disabled = false;
        btn.textContent = 'Generate MCQs';
    }
}

// Poll for MCQ generation status
function pollGenerationStatus(mcqSetId) {
    const pollInterval = setInterval(async () => {
        try {
            const response = await fetch(`/api/mcq-sets/${mcqSetId}`);
            const data = await response.json();
            const status = data.mcq_set.status;
            
            if (status === 'done' || status === 'failed') {
                clearInterval(pollInterval);
                window.location.reload();
            }
        } catch (error) {
            console.error('Polling error:', error);
            clearInterval(pollInterval);
        }
    }, 2000);
}

// Quiz - Submit
async function handleQuizSubmit(event) {
    event.preventDefault();
    
    // Validate all questions are answered
    const form = event.target;
    const formData = new FormData(form);
    
    try {
        const response = await fetch('/api/quiz/submit', {
            method: 'POST',
            body: formData
        });
        
        if (response.ok) {
            window.location.href = '/quiz/results';
        } else {
            const error = await response.json();
            alert(error.detail || 'Submission failed');
        }
    } catch (error) {
        alert('Submission failed: ' + error.message);
    }
}

// Close modal when clicking outside
window.onclick = function(event) {
    const uploadModal = document.getElementById('uploadModal');
    const editModal = document.getElementById('editModal');
    
    if (event.target === uploadModal) {
        closeUploadModal();
    }
    if (event.target === editModal) {
        closeEditModal();
    }
}

// Loading modal functions
function showLoading(message) {
    console.log('showLoading called with:', message);
    const modal = document.getElementById('loadingModal');
    console.log('Modal element:', modal);
    const messageEl = document.getElementById('loadingMessage');
    if (messageEl) {
        messageEl.textContent = message;
    }
    if (modal) {
        modal.classList.add('active');
        console.log('Added active class, modal classes:', modal.className);
    } else {
        console.error('Loading modal not found!');
    }
}

function hideLoading() {
    const modal = document.getElementById('loadingModal');
    if (modal) {
        modal.classList.remove('active');
    }
}
