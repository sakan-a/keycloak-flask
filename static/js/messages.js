const searchBox = document.getElementById('search-box');
const resultsList = document.getElementById('search-results');

searchBox.addEventListener('input', async function () {
    const query = this.value.trim();
    if (!query) {
        resultsList.innerHTML = '';
        return;
    }

    try {
        const response = await fetch(`/search_messages?q=${encodeURIComponent(query)}`);
        const users = await response.json();

        resultsList.innerHTML = '';
        if (users.length > 0) {
            users.forEach(user => {
                const li = document.createElement('li');
                li.innerHTML = `<a href='${"/messages/" + user.username}'>${user.username}</a>`;
                resultsList.appendChild(li);
            });
        } else {
            const li = document.createElement('li');
            li.textContent = 'No users found.';
            resultsList.appendChild(li);
        }
    } catch (err) {
        resultsList.innerHTML = '<li>Error searching users.</li>';
    }
});