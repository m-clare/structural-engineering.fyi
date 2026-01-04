const apiUrl = "http://localhost:8000/licensees";

const licenses = await fetch(apiUrl).then((response) => {
  if (!response.ok) {
    throw new Error(response.status);
  }
  return response.json();
});

process.stdout.write(JSON.stringify(licenses));
