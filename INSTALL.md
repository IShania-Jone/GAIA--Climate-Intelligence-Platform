
# Installation Guide for GAIA-∞

## Prerequisites

1. Python 3.8 or higher
2. Google Earth Engine account
3. Access to Google Cloud Platform (for full functionality)

## Environment Setup

1. Create a copy of `.env.example` as `.env` and fill in your credentials:
   ```
   EARTH_ENGINE_SERVICE_ACCOUNT=your-service-account@project.iam.gserviceaccount.com
   EARTH_ENGINE_PRIVATE_KEY=your-private-key
   ```

2. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Google Earth Engine Setup

1. Create a Google Earth Engine account at https://earthengine.google.com/
2. Set up a service account and download credentials
3. Add credentials to your `.env` file

## Running the Application

1. Start the main application:
   ```bash
   streamlit run app.py
   ```

2. Access the application at: http://localhost:5000

## Troubleshooting

### Common Issues

1. Earth Engine Authentication:
   - Verify credentials in `.env` file
   - Ensure service account has proper permissions

2. Dependencies:
   - Run `pip install -r requirements.txt` again
   - Check Python version compatibility

### Support

For additional help, please open an issue on the GitHub repository.
