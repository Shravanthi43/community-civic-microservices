const API_URL = "http://localhost:5000";

document.getElementById("wardForm").addEventListener("submit", async function(event) {
    event.preventDefault();

    const wardNumber = document.getElementById("wardNumber").value.trim();
    const wardName = document.getElementById("wardName").value.trim();
    const area = document.getElementById("area").value.trim();

    try {
        const response = await fetch(API_URL + "/wards", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                ward_number: wardNumber,
                ward_name: wardName,
                area: area
            })
        });

        const data = await response.json();

        if (response.ok) {
            document.getElementById("result").innerHTML =
                `<div class="success">
                    <h3>Ward Added Successfully ✓</h3>
                    Ward ID: ${data.ward_id}<br>
                    Ward Number: ${data.ward_number}<br>
                    Ward Name: ${data.ward_name}<br>
                    Area: ${data.area}
                </div>`;

            document.getElementById("wardForm").reset();
        } else {
            document.getElementById("result").innerHTML =
                `<div class="error">
                    <h3>Error</h3>
                    ${data.error}
                </div>`;
        }

    } catch (error) {
        document.getElementById("result").innerHTML =
            `<div class="error">
                Unable to connect to Ward Service
            </div>`;
    }
});


async function findWardByNumber() {
    const wardNumber =
        document.getElementById("searchWardNumber").value.trim();

    if (!wardNumber) {
        document.getElementById("wardDetails").innerHTML =
            "<p>Please enter a ward number.</p>";
        return;
    }

    try {
        const response = await fetch(
            API_URL + "/wards/number/" +
            encodeURIComponent(wardNumber)
        );

        const data = await response.json();

        if (response.ok) {
            document.getElementById("wardDetails").innerHTML =
                `<div class="success">
                    <h3>Ward Exists ✓</h3>
                    Ward ID: ${data.ward_id}<br>
                    Ward Number: ${data.ward_number}<br>
                    Ward Name: ${data.ward_name}<br>
                    Area: ${data.area}
                </div>`;
        } else {
            document.getElementById("wardDetails").innerHTML =
                `<div class="error">
                    <h3>Ward Does Not Exist ✗</h3>
                    ${data.error}
                </div>`;
        }

    } catch (error) {
        document.getElementById("wardDetails").innerHTML =
            `<div class="error">
                Unable to connect to Ward Service
            </div>`;
    }
}


async function findWard() {
    const id =
        document.getElementById("searchWardId").value;

    if (!id) {
        document.getElementById("wardIdDetails").innerHTML =
            "<p>Please enter a Ward ID.</p>";
        return;
    }

    try {
        const response = await fetch(API_URL + "/wards/" + id);
        const data = await response.json();

        if (response.ok) {
            document.getElementById("wardIdDetails").innerHTML =
                `<div class="success">
                    <h3>Ward Details</h3>
                    Ward ID: ${data.ward_id}<br>
                    Ward Number: ${data.ward_number}<br>
                    Ward Name: ${data.ward_name}<br>
                    Area: ${data.area}
                </div>`;
        } else {
            document.getElementById("wardIdDetails").innerHTML =
                `<div class="error">${data.error}</div>`;
        }

    } catch (error) {
        document.getElementById("wardIdDetails").innerHTML =
            `<div class="error">
                Unable to connect to Ward Service
            </div>`;
    }
}


async function getAllWards() {
    try {
        const response = await fetch(API_URL + "/wards");
        const data = await response.json();

        if (response.ok) {

            if (data.length === 0) {
                document.getElementById("allWards").innerHTML =
                    "<p>No wards registered yet.</p>";
                return;
            }

            let html = "<h3>All Wards</h3>";

            data.forEach(function(ward) {
                html += `
                    <div class="ward-card">
                        <strong>Ward ID:</strong> ${ward.ward_id}<br>
                        <strong>Ward Number:</strong> ${ward.ward_number}<br>
                        <strong>Ward Name:</strong> ${ward.ward_name}<br>
                        <strong>Area:</strong> ${ward.area}
                    </div>
                `;
            });

            document.getElementById("allWards").innerHTML = html;

        } else {
            document.getElementById("allWards").innerHTML =
                `<div class="error">${data.error}</div>`;
        }

    } catch (error) {
        document.getElementById("allWards").innerHTML =
            `<div class="error">
                Unable to connect to Ward Service
            </div>`;
    }
}

async function testRateLimit() {

    const result = document.getElementById("rateLimitResult");
    const requestInput = document.getElementById("requestCount");

    const totalRequests = parseInt(requestInput.value);

    if (!totalRequests || totalRequests < 1) {
        result.innerHTML = `
            <p class="error">Please enter a valid number of requests.</p>
        `;
        return;
    }

    result.innerHTML = "Testing rate limit... Please wait.";

    let successful = 0;
    let rateLimited = 0;
    let failed = 0;

    const requests = [];

    for (let i = 0; i < totalRequests; i++) {

        requests.push(
            fetch(`${API_URL}/wards`)
                .then(response => {

                    if (response.status === 429) {
                        rateLimited++;
                    }
                    else if (response.ok) {
                        successful++;
                    }
                    else {
                        failed++;
                    }

                })
                .catch(() => {
                    failed++;
                })
        );

    }

    await Promise.all(requests);

    result.innerHTML = `
        <h3>Rate Limit Test Result</h3>

        <p>Total Requests: ${totalRequests}</p>

        <p>Successful Requests: ${successful}</p>

        <p>Rate Limited (429): ${rateLimited}</p>

        <p>Other Failed Requests: ${failed}</p>
    `;
}