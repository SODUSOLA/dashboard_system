# Interactive Sales Dashboard

A powerful, AI-enhanced business intelligence platform built with Streamlit that transforms raw data into actionable insights through automated analysis, interactive visualizations, and professional reporting.

## Features

### Core Functionality
- **Data Upload & Processing**: Support for CSV and Excel files with intelligent data cleaning
- **AI-Powered Analytics**: Automated KPI discovery using Google Gemini AI
- **Interactive Dashboard Builder**: Drag-and-drop chart configuration with 10+ visualization types
- **Professional Exports**: Generate polished HTML reports or live web dashboards
- **Session Management**: Persistent data across page navigation

### Visualization Types
- Bar Charts
- Line Charts
- Area Charts
- Scatter Plots
- Pie Charts
- Histograms
- Box Plots
- Violin Plots
- Heatmaps
- Bubble Charts

### AI Features
- **Smart KPI Suggestions**: Automatically identifies key performance indicators from your data
- **Chart Insights**: AI-generated business insights for each visualization
- **Intelligent Data Cleaning**: Automated preprocessing with memory optimization

## Technology Stack

- **Frontend**: Streamlit
- **Data Processing**: Pandas, NumPy
- **Visualization**: Plotly
- **AI Integration**: Google Gemini 2.0 Flash
- **Export Features**: HTML/CSS, Live Server
- **File Handling**: CSV, Excel support

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/sales-dashboard.git
   cd sales-dashboard
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   Create a `.env` file in the root directory:
   ```
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

4. **Run the application**:
   ```bash
   streamlit run app.py
   ```

## Usage

### Getting Started
1. **Upload Data**: Start by uploading your CSV or Excel file
2. **Data Cleaning**: The system automatically cleans and preprocesses your data
3. **KPI Discovery**: Generate AI-powered KPI suggestions
4. **Configure Dashboard**: Select chart types, KPIs, and grouping options
5. **View Dashboard**: Explore your interactive visualizations
6. **Export Results**: Download HTML reports or launch live dashboards

### Dashboard Configuration
- Choose from 10+ chart types
- Select KPIs from numeric columns
- Group data by categorical columns
- Customize colors (plain or randomized)
- Add custom chart labels

### Export Options
- **HTML Download**: Professional static reports with embedded charts
- **Live Server**: Interactive web dashboards served locally
- **Chart Images**: Individual PNG exports for each visualization

## Project Structure

```
sales_dashboard/
├── app.py                      # Main application entry point
├── requirements.txt            # Python dependencies
├── dashboard_export.html       # Sample exported dashboard
├── pages/
│   ├── dashboard_config.py     # Chart configuration interface
│   └── dis_view.py            # Dashboard insights system view
├── utils/
│   ├── data_cleaner.py        # Data preprocessing utilities
│   ├── file_handler.py        # File upload and reading
│   ├── gemini_client.py       # AI integration client
│   ├── kpi_engine.py          # Chart generation engine
│   └── session_manager.py     # Session state management
├── exports/
│   ├── export_engine.py       # Export functionality interface
│   ├── html_exporter.py       # HTML dashboard generation
│   └── live_server.py        # Local server for live dashboards
└── fonts/                     # Font files for PDF exports
```

## Configuration

### Environment Variables
- `GEMINI_API_KEY`: Your Google Gemini API key for AI features

### Customization Options
- Chart color schemes (plain vs randomized)
- Export templates and branding
- Data cleaning parameters
- Memory optimization settings

## Data Requirements

### Supported Formats
- CSV files
- Excel files (.xlsx, .xls)

### Data Quality Features
- Automatic missing value handling
- Duplicate removal
- Data type optimization
- Outlier detection and removal
- Memory usage optimization

## AI Integration

### Gemini AI Features
- **KPI Discovery**: Analyzes dataset structure to suggest relevant metrics
- **Chart Insights**: Provides business context and recommendations for each visualization
- **Intelligent Grouping**: Suggests optimal data aggregations

### API Usage
The application uses Google Gemini 2.0 Flash for:
- Natural language processing of data structures
- Business intelligence recommendations
- Automated insight generation

## Dashboard Features

### Interactive Elements
- Real-time chart updates
- Drill-down capabilities
- Data filtering and sorting
- Export functionality

### Professional Design
- Responsive layout
- Modern UI components
- Customizable branding
- Print-ready reports

## Future Updates

### Planned Features
- **Advanced Analytics**
  - Predictive modeling
  - Trend analysis
  - Anomaly detection
  - Statistical testing

- **Enhanced Visualization**
  - 3D charts
  - Geographic mapping
  - Real-time data streaming
  - Custom chart themes

- **Collaboration Features**
  - Multi-user dashboards
  - Shared workspaces
  - Commenting system
  - Version control

- **Integration Capabilities**
  - Database connections (PostgreSQL, MySQL, MongoDB)
  - API endpoints for data ingestion
  - Cloud storage integration
  - Third-party BI tool connections

- **Mobile & Accessibility**
  - Mobile-responsive design
  - PWA support
  - Screen reader compatibility
  - Keyboard navigation

- **Performance Enhancements**
  - Big data processing
  - Caching mechanisms
  - Parallel processing
  - GPU acceleration for visualizations

- **Security & Compliance**
  - User authentication
  - Data encryption
  - GDPR compliance
  - Audit logging

- **AI Enhancements**
  - Custom AI models
  - Natural language queries
  - Automated report generation
  - Voice commands

### Development Roadmap
1. **Q4 2025**: Advanced analytics and predictive features
2. **Q1 2026**: Collaboration tools and multi-user support
3. **Q2 2026**: Mobile app development
4. **Q3 2026**: Enterprise features and API integrations

## Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Made with ❤️ for data-driven decision making**
