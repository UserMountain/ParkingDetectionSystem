# Vehicle Parking Patrol System (VPPS)

Vehicle Parking Patrol System (VPPS) is a web application designed to monitor parking areas using drone image capture and license plate recognition. The application consists of multiple pages for live streaming, image upload, patrol scheduling, system logs, and vehicle management.

## Features

- **Live Streaming**: Stream live footage from a drone.
- **Image Upload**: Upload images and extract license plate information.
- **Patrol Schedule**: Manage and view patrol schedules.
- **System Logs**: View system logs and activities.
- **Vehicle Management**: Manage vehicle data and view uploaded images.

## Installation

1. **Clone the Repository**:
    ```bash
    git clone https://github.com/yourusername/vpps.git
    cd vpps
    ```

2. **Create and Activate a Virtual Environment**:
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
    ```

3. **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4. **Set Up the Database**:
    ```bash
    flask db init
    flask db migrate -m "Initial migration"
    flask db upgrade
    ```

5. **Run the Application**:
    ```bash
    python app.py
    ```

6. **Access the Application**:
    Open your web browser and go to `http://127.0.0.1:5000`.

## Project Structure

