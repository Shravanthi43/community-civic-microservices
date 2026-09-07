const API_URL = "http://localhost:5003";


// ---------------------------------------------------------------
// Add Ward
// ---------------------------------------------------------------

document.getElementById("wardForm")
    .addEventListener("submit", async function(event) {

        event.preventDefault();

        const wardNumber = document.getElementById("wardNumber").value;
        const wardName = document.getElementById("wardName").value;
        const area = document.getElementById("area").value;

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
                    `<h3>Ward Added Successfully</h3>
                    Ward ID: ${data.ward_id}<br>
                    Ward Number: ${data.ward_number}<br>
                    Ward Name: ${data.ward_name}<br>
                    Area: ${data.area}`;

                document.getElementById("wardForm").reset();

            } else {

                document.getElementById("result").innerHTML =
                    `<h3>Error</h3>${data.error}`;

            }

        } catch (error) {

            document.getElementById("result").innerHTML =
                `<h3>Error</h3>
                Unable to connect to Ward Service`;

        }
    });


// ---------------------------------------------------------------
// Find Ward
// ---------------------------------------------------------------

async function findWard() {

    const id = document.getElementById("searchWardId").value;

    try {

        const response = await fetch(
            API_URL + "/wards/" + id
        );

        const data = await response.json();

        if (response.ok) {

            document.getElementById("wardDetails").innerHTML =
                `<h3>Ward Details</h3>
                Ward ID: ${data.ward_id}<br>
                Ward Number: ${data.ward_number}<br>
                Ward Name: ${data.ward_name}<br>
                Area: ${data.area}`;

        } else {

            document.getElementById("wardDetails").innerHTML =
                `<h3>Error</h3>${data.error}`;

        }

    } catch (error) {

        document.getElementById("wardDetails").innerHTML =
            `<h3>Error</h3>
            Unable to connect to Ward Service`;

    }
}


// ---------------------------------------------------------------
// Get All Wards
// ---------------------------------------------------------------

async function getAllWards() {

    try {

        const response = await fetch(
            API_URL + "/wards"
        );

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
                    <div>
                        <strong>Ward ID:</strong> ${ward.ward_id}<br>
                        <strong>Ward Number:</strong> ${ward.ward_number}<br>
                        <strong>Ward Name:</strong> ${ward.ward_name}<br>
                        <strong>Area:</strong> ${ward.area}
                    </div>
                    <hr>
                `;
            });

            document.getElementById("allWards").innerHTML = html;

        } else {

            document.getElementById("allWards").innerHTML =
                `<h3>Error</h3>${data.error}`;

        }

    } catch (error) {

        document.getElementById("allWards").innerHTML =
            `<h3>Error</h3>
            Unable to connect to Ward Service`;

    }
}