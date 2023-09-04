function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Get a reference to the map container
const mapContainer = document.getElementById('map');

// Set the container's width to 100%
mapContainer.style.width = '100%';

const map = new mapboxgl.Map({
    container: 'map',
    style: 'mapbox://styles/mapbox/streets-v12', // Replace with your desired map style
    center: [14.360334967044373, 53.773164937329774], // Longitude and latitude
    zoom: 3, // Zoom level
    projection: 'mercator', // Projection
});

map.addControl(new mapboxgl.NavigationControl());

// Add geolocate control to the map.
map.addControl(
    new mapboxgl.GeolocateControl({
        positionOptions: {
            enableHighAccuracy: true
        },
        // When active the map will receive updates to the device's location as it changes.
        trackUserLocation: true,
        // Draw an arrow next to the location dot to indicate which direction the device is heading.
        showUserHeading: false
    })
);

// Create an object to keep track of the visibility state of each category
const categoryVisibility = {};
const urlParams = new URLSearchParams(window.location.search);
const queryCategoryNumber = urlParams.get('category');
const queryCategory = parseInt(queryCategoryNumber, 10);
// console.log(typeof (queryCategory));

const queryUserNumber = urlParams.get('user_id');
const queryUser = parseInt(queryUserNumber, 10);
// console.log('queryUser '+queryUser)

map.on('load', () => {
    fetch('http://127.0.0.1:8000/api') // Replace with the actual URL for fetching your data.
        .then(response => response.json())
        .then(data => {
            // console.log('data '+data);
            const categories = {};

            data.forEach(item => {
                const userId = item.user;
                const category = item.category;
                console.log('category '+category);
                console.log('user ' +userId)

                // Only proceed if the item's category matches the queryCategory
                if ((queryCategory && category !== queryCategory) || (queryUser && userId !== queryUser)) {
                    return;
                }

                if (!categories[category]) {
                    categories[category] = {
                        type: 'FeatureCollection',
                        features: []
                    };
                }

                categories[category].features.push({
                    type: 'Feature',
                    geometry: {
                        type: 'Point',
                        coordinates: [item.longitude, item.latitude]
                    },
                    properties: {
                        title: item.title,
                        description: item.description
                    }
                });
            });

            // Now you have the filtered categories based on queryCategory
            console.log(categories);

            Object.keys(categories).forEach(category => {
                const categoryId = parseInt(category, 10);
                const sourceId = `locations-${category}`;
                let circleColor = '#DC143C';

                if (categoryId === 1) {
                    circleColor = '#3399FF';
                } else if (categoryId === 2) {
                    circleColor = '#66CC99';
                } else if (categoryId === 4) {
                    circleColor = '#004080';
                } else if (categoryId === 3) {
                    circleColor = '#00A0C6';
                } else if (categoryId === 5) {
                    circleColor = '#40E0D0';
                } else if (categoryId === 6) {
                    circleColor = '#008080';
                }

                map.addSource(sourceId, {
                    type: 'geojson',
                    data: categories[category]
                });

                map.addLayer({
                    id: `locations-${category}`,
                    type: 'circle',
                    source: sourceId,
                    layout: {
                        visibility: 'visible'
                    },
                    paint: {
                        'circle-radius': 8,
                        'circle-color': circleColor,
                        'circle-stroke-width': 2,
                        'circle-stroke-color': '#ffffff'
                    }
                });

                // Add popup event listeners here
                map.on('click', `locations-${category}`, (e) => {
                    console.log('Popup event listener triggered.');
                    e.originalEvent.preventDefault();
                    const coordinates = e.features[0].geometry.coordinates.slice();
                    const description = e.features[0].properties.description;

                    while (Math.abs(e.lngLat.lng - coordinates[0]) > 180) {
                        coordinates[0] += e.lngLat.lng > coordinates[0] ? 360 : -360;
                    }

                    new mapboxgl.Popup()
                        .setLngLat(coordinates)
                        .setHTML(`<h3>${e.features[0].properties.title}</h3><p>${description}</p>`)
                        .addTo(map);
                });

                // Change the cursor to a pointer when the mouse is over the category layer.
                map.on('mouseenter', `locations-${category}`, () => {
                    map.getCanvas().style.cursor = 'pointer';
                });

                // Change it back to a pointer when it leaves.
                map.on('mouseleave', `locations-${category}`, () => {
                    map.getCanvas().style.cursor = '';
                });
            });

            // Add event listeners to the category buttons outside the loop
            const categoryButtons = document.querySelectorAll('#category-menu button');

            categoryButtons.forEach(button => {
                button.addEventListener('click', () => {
                    const selectedCategory = button.id;

                    if (selectedCategory === 'all') {
                        // Toggle visibility for all categories
                        toggleAllCategories();
                    } else {
                        // Toggle layers based on the selected category
                        toggleLayers(selectedCategory);
                    }
                });
            });

            function toggleAllCategories() {
                const toggleableLayerIds = Object.keys(categories).map(category => `locations-${category}`);

                toggleableLayerIds.forEach(layerId => {
                    if (!categoryVisibility[layerId]) {
                        categoryVisibility[layerId] = 'visible';
                    }

                    if (categoryVisibility[layerId] === 'visible') {
                        map.setLayoutProperty(layerId, 'visibility', 'none');
                        categoryVisibility[layerId] = 'none';
                    } else {
                        map.setLayoutProperty(layerId, 'visibility', 'visible');
                        categoryVisibility[layerId] = 'visible';
                    }
                });
            }

            function toggleLayers(selectedCategory) {
                const toggleableLayerIds = Object.keys(categories).map(category => `locations-${category}`);

                toggleableLayerIds.forEach(layerId => {
                    if (!categoryVisibility[layerId]) {
                        categoryVisibility[layerId] = 'visible';
                    }

                    if (selectedCategory === layerId.split('-')[1]) {
                        if (categoryVisibility[layerId] === 'visible') {
                            map.setLayoutProperty(layerId, 'visibility', 'none');
                            categoryVisibility[layerId] = 'none';
                        } else {
                            map.setLayoutProperty(layerId, 'visibility', 'visible');
                            categoryVisibility[layerId] = 'visible';
                        }
                    } else {
                        if (categoryVisibility[layerId] === 'visible') {
                            map.setLayoutProperty(layerId, 'visibility', 'visible');
                        }
                    }
                });
            }


            map.on('click', function (e) {
                    if (!e.originalEvent.defaultPrevented) {
                        // click was performed outside of layer_1
                        e.originalEvent.preventDefault();
                        // Open the modal when clicking on the map
                        $('#addMarkerModal').modal('show');

                        // Display the coordinates in the input fields in the modal
                        $('#latitudeInput').val(e.lngLat.lat.toFixed(6));
                        $('#longitudeInput').val(e.lngLat.lng.toFixed(6));

                        $('#userId').val(queryUser);

                        // Handle form submission and adding marker when the modal form is submitted
                        $('#addMarkerForm').submit(function (event) {
                            event.preventDefault();

                            // Extract form data
                            const title = $('#title').val();
                            const description = $('#description').val();
                            const latitude = $('#latitudeInput').val();
                            const longitude = $('#longitudeInput').val();
                            const category = $('#categorySelect').val();
                            const image = $('#imageInput')[0].files[0];
                            const user = $('#userId').val();


                            // Close the modal after extracting data
                            $('#addMarkerModal').modal('hide');

                            // Use FormData to send the data including the image
                            const formData = new FormData();
                            formData.append('title', title);
                            formData.append('description', description);
                            formData.append('latitude', latitude);
                            formData.append('longitude', longitude);
                            formData.append('category', category);
                            formData.append('image', image);  // Append the image file
                            formData.append('user', user);

                            // Use AJAX or fetch to send the data to your Django API
                            const csrftoken = getCookie('XSRF-TOKEN');
                            $.ajax({
                                method: 'POST',
                                url: 'http://127.0.0.1:8000/api',
                                mode: 'same-origin',
                                headers: {
                                    "Accept": "application/json",
                                    'X-CSRFToken': csrftoken
                                },
                                data: formData,  // Send FormData with image
                                processData: false,  // Important: prevent jQuery from processing the data
                                contentType: false,  // Important: prevent jQuery from setting the content type
                                success: function (response) {
                                    console.log(response);
                                    window.location.reload();
                                },
                            });
                        });
                    }
                }
            )

        })
        .catch(error => console.error('Error fetching data:', error));
});




