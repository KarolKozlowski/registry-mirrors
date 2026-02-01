// async function fetchAndRender() {
//     const container = document.getElementById('registryListing');
//     try {
//     const response = await fetch('/registries/');
//     if (!response.ok) throw new Error('Network response was not ok');
//     const data = await response.json();

//     container.innerHTML = ''; // clear loading text

//     if (Array.isArray(data) && data.length > 0) {
//         data.forEach(entry => {
//         const div = document.createElement('div');
//         div.className = 'entry ' + (entry.type === 'registry' ? 'registry' : '');
//         div.innerHTML = `
//             <a href="${entry.name}/">${entry.name}</a>
//         `;
//         container.appendChild(div);
//         });
//     } else {
//         container.textContent = 'No entries found.';
//     }
//     } catch (error) {
//     container.textContent = 'Failed to load directory listing: ' + error.message;
//     }
// }

// fetchAndRender();


    async function loadCatalogElements() {
      const container = document.getElementById('registryListing');
      const sourceUrl = 'https://registry.np.dotnot.pl/'; // registry-url
      const catalogPath = 'registries'; // catalog path

      try {
        const response = await fetch(`${sourceUrl}${catalogPath}`);
        if (!response.ok) throw new Error('Failed to fetch catalog data');
        const catalog = await response.json();

        container.innerHTML = ''; // Clear loading text

        if (Array.isArray(catalog) && catalog.length > 0) {
          catalog.forEach(item => {
            // Create catalog-element container div
            const catalogElem = document.createElement('catalog-element');

            // Create content div
            const contentDiv = document.createElement('div');
            contentDiv.className = 'content';

            // Create material-card
            const materialCard = document.createElement('material-card');
            materialCard.className = 'list highlight';
            // materialCard.style.zIndex = '2';

            // Anchor link to taglist path
            const anchor = document.createElement('a');
            anchor.href = `${sourceUrl}/${item.name}`;

            // material-waves with nested div#waves
            const materialWaves = document.createElement('material-waves');

            const wavesDiv = document.createElement('div');
            wavesDiv.id = 'waves';

            materialWaves.appendChild(wavesDiv);
            anchor.appendChild(materialWaves);
            materialCard.appendChild(anchor);

            
            // Span info with icon and repository/tag count
            const infoSpan = document.createElement('span');
            infoSpan.innerHTML = `
            <i class="material-icons">send</i>
                ${item.name}
                <div class="item-count right">${anchor.href || 'N/A'}<i class="material-icons animated"></i></div>`;
            
            materialCard.appendChild(infoSpan);
            contentDiv.appendChild(materialCard);
            catalogElem.appendChild(contentDiv);
            container.appendChild(catalogElem);
          });
        } else {
          container.textContent = 'No registry proxies found.';
        }
      } catch (error) {
        container.textContent = 'Error loading registries: ' + error.message;
      }
    }

    loadCatalogElements();