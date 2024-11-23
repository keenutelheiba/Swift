document.addEventListener('DOMContentLoaded', function() {
  const fromInput = document.getElementById('rfrom');
  const toInput = document.getElementById('to');
  const fromIdInput = document.getElementById('rfrom_id');
  const toIdInput = document.getElementById('to_id');
  const fromResults = document.getElementById('fromResults');
  const toResults = document.getElementById('toResults');

  let selectedIndex = -1;

  function handleKeyNavigation(e, resultsDiv, input, idInput) {
    const items = resultsDiv.getElementsByClassName('search-result-item');
    
    if (items.length === 0) return;

    // Remove previous selection
    if (selectedIndex >= 0 && selectedIndex < items.length) {
      items[selectedIndex].classList.remove('selected');
    }

    switch(e.key) {
      case 'ArrowDown':
        e.preventDefault();
        selectedIndex = (selectedIndex + 1) % items.length;
        break;
      case 'ArrowUp':
        e.preventDefault();
        selectedIndex = selectedIndex <= 0 ? items.length - 1 : selectedIndex - 1;
        break;
      case 'Enter':
        e.preventDefault();
        if (selectedIndex >= 0) {
          const selectedItem = items[selectedIndex];
          input.value = selectedItem.textContent;
          idInput.value = selectedItem.dataset.id;
          resultsDiv.style.display = 'none';
          selectedIndex = -1;
        }
        return;
    }

    // Add selection to new item
    if (selectedIndex >= 0) {
      items[selectedIndex].classList.add('selected');
      items[selectedIndex].scrollIntoView({ block: 'nearest' });
    }
  }

  async function searchStations(query) {
    if (!query.trim()) return [];
    try {
      const response = await fetch(`/api/search-stations?q=${encodeURIComponent(query)}`);
      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error fetching stations:', error);
      return [];
    }
  }

  function displayResults(results, resultsDiv, displayInput, idInput) {
    resultsDiv.innerHTML = '';
    selectedIndex = -1;
    
    if (results.length === 0) {
      resultsDiv.style.display = 'none';
      return;
    }

    results.forEach(station => {
      const div = document.createElement('div');
      div.className = 'search-result-item';
      div.textContent = `${station.name}, ${station.place}`;
      div.dataset.id = station.id;
      div.addEventListener('click', () => {
        displayInput.value = `${station.name}, ${station.place}`;
        idInput.value = station.id;
        resultsDiv.style.display = 'none';
      });
      resultsDiv.appendChild(div);
    });
    resultsDiv.style.display = 'block';
  }

  // Add keyboard event listeners
  fromInput.addEventListener('keydown', (e) => handleKeyNavigation(e, fromResults, fromInput, fromIdInput));
  toInput.addEventListener('keydown', (e) => handleKeyNavigation(e, toResults, toInput, toIdInput));

  // Add input event listeners
  fromInput.addEventListener('input', async () => {
    const results = await searchStations(fromInput.value);
    displayResults(results, fromResults, fromInput, fromIdInput);
  });

  toInput.addEventListener('input', async () => {
    const results = await searchStations(toInput.value);
    displayResults(results, toResults, toInput, toIdInput);
  });

  // Close results when clicking outside
  document.addEventListener('click', (e) => {
    if (!e.target.closest('.station-search-container')) {
      fromResults.style.display = 'none';
      toResults.style.display = 'none';
      selectedIndex = -1;
    }
  });
}); 