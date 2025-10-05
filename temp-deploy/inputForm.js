const { useState, useEffect, useMemo, useRef } = React;
const { MapContainer, TileLayer, Marker, useMapEvents } = ReactLeaflet;

// Fix for default icon issue with Leaflet in React
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-shadow.png',
});


// --- Helper Components ---

const Stepper = ({ currentStep }) => {
  const steps = ['Location', 'Dates', 'Activity', 'Report'];
  return (
    <div style={styles.stepperContainer}>
      {steps.map((step, index) => (
        <React.Fragment key={step}>
          <div style={styles.stepWrapper}>
            <div style={{
              ...styles.stepCircle,
              backgroundColor: currentStep > index + 1 || currentStep === index + 1 ? '#007bff' : '#e9ecef',
              color: currentStep > index + 1 || currentStep === index + 1 ? '#fff' : '#6c757d',
            }}>
              {currentStep > index + 1 ? '✓' : index + 1}
            </div>
            <div style={{
                ...styles.stepLabel,
                color: currentStep === index + 1 ? '#007bff' : '#6c757d',
            }}>{step}</div>
          </div>
          {index < steps.length - 1 && <div style={styles.stepConnector} />}
        </React.Fragment>
      ))}
    </div>
  );
};

const Tab = ({ label, isActive, onClick }) => (
    <button style={{...styles.tab, ...(isActive ? styles.activeTab : {})}} onClick={onClick}>
        {label}
    </button>
);


// --- Step 1: Location ---

const DraggableMarker = ({ position, setPosition, setLocation }) => {
    const markerRef = useRef(null);
    const map = useMapEvents({
        click(e) {
            setPosition(e.latlng);
            setLocation({ name: `Custom Pin: ${e.latlng.lat.toFixed(4)}, ${e.latlng.lng.toFixed(4)}`, lat: e.latlng.lat, lng: e.latlng.lng });
        },
    });

    const eventHandlers = useMemo(
        () => ({
            dragend() {
                const marker = markerRef.current;
                if (marker != null) {
                    const newPos = marker.getLatLng();
                    setPosition(newPos);
                    setLocation({ name: `Custom Pin: ${newPos.lat.toFixed(4)}, ${newPos.lng.toFixed(4)}`, lat: newPos.lat, lng: newPos.lng });
                }
            },
        }),
        [setPosition, setLocation],
    );
    
    useEffect(() => {
        map.flyTo(position, map.getZoom());
    }, [position, map]);

    return (
        <Marker
            draggable={true}
            eventHandlers={eventHandlers}
            position={position}
            ref={markerRef}
        />
    );
};

const LocationStep = ({ location, setLocation }) => {
    const [searchTerm, setSearchTerm] = useState(location.name || "");
    const [suggestions, setSuggestions] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    // Default position set to Chicago (Millennium Park)
    const [position, setPosition] = useState({ lat: 41.8826, lng: -87.6227 });
    const [isDropdownVisible, setIsDropdownVisible] = useState(true);

    const fetchSuggestions = async (query) => {
        if (!query) {
            setSuggestions([]);
            return;
        }
        setIsLoading(true);
        
        // --- MOCK API FOR DEMONSTRATION ---
        await new Promise(resolve => setTimeout(resolve, 500)); // Simulate network delay
        const mockSuggestions = [
            { name: 'Millennium Park, Chicago, IL', lat: 41.8826, lng: -87.6227 },
            { name: 'Navy Pier, Chicago, IL', lat: 41.8917, lng: -87.6099 },
            { name: 'Wrigleyville, Chicago, IL', lat: 41.9484, lng: -87.6553 },
            { name: 'Lincoln Park Zoo, Chicago, IL', lat: 41.9213, lng: -87.6339 },
            { name: 'The Art Institute of Chicago, IL', lat: 41.8796, lng: -87.6237 },
        ].filter(s => s.name.toLowerCase().includes(query.toLowerCase()));
        setSuggestions(mockSuggestions);
        setIsLoading(false);
    };

    useEffect(() => {
        if (searchTerm && searchTerm !== location.name) {
            const debounceTimeout = setTimeout(() => fetchSuggestions(searchTerm), 300);
            return () => clearTimeout(debounceTimeout);
        }
    }, [searchTerm, location.name]);

    const handleSelectSuggestion = (suggestion) => {
        setLocation(suggestion);
        setSearchTerm(suggestion.name);
        setPosition({ lat: suggestion.lat, lng: suggestion.lng });
        setSuggestions([]);
        setIsDropdownVisible(false);
    };

    const handleSearchChange = (e) => {
        setSearchTerm(e.target.value);
        setIsDropdownVisible(true);
    };
    
    const handleUseCurrentLocation = () => {
        navigator.geolocation.getCurrentPosition(
            (pos) => {
                const { latitude, longitude } = pos.coords;
                const newPos = { lat: latitude, lng: longitude };
                setPosition(newPos);
                const newLocation = { name: `Your Location: ${latitude.toFixed(4)}, ${longitude.toFixed(4)}`, ...newPos};
                setLocation(newLocation);
                setSearchTerm(newLocation.name);
                setIsDropdownVisible(false);
            },
            () => {
                alert("Could not get your location. Please enable location services in your browser.");
            }
        );
    };

    return (
        <div style={styles.stepContainer}>
            <h2 style={styles.header}>📍 Choose a Location in Chicago</h2>
             <div style={styles.locationControls}>
                <div style={{...styles.inputGroup, flex: 1}}>
                    <input
                        type="text"
                        style={styles.searchInput}
                        placeholder="e.g., Millennium Park, Wrigleyville"
                        value={searchTerm}
                        onChange={handleSearchChange}
                        onFocus={() => setIsDropdownVisible(true)}
                    />
                    {isLoading && <div style={styles.autocompleteDropdown}>Loading...</div>}
                    {isDropdownVisible && suggestions.length > 0 && (
                        <div style={styles.autocompleteDropdown}>
                            {suggestions.map(s => (
                                <div key={s.name} style={styles.autocompleteItem} onClick={() => handleSelectSuggestion(s)}>
                                   {s.name}
                                </div>
                            ))}
                        </div>
                    )}
                </div>
                <button onClick={handleUseCurrentLocation} style={styles.locationButton} title="Use my current location">
                    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 2L12 2A9.5 9.5 0 0 1 21.5 11.5L21.5 11.5"/><path d="M22 12L22 12A9.5 9.5 0 0 1 12.5 21.5L12.5 21.5"/><path d="M12 22L12 22A9.5 9.5 0 0 1 2.5 12.5L2.5 12.5"/><path d="M2 12L2 12A9.5 9.5 0 0 1 11.5 2.5L11.5 2.5"/></svg>
                </button>
            </div>
            
            <div style={styles.mapContainer}>
                <MapContainer center={position} zoom={12} style={{ height: '100%', width: '100%' }}>
                    <TileLayer
                        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                    />
                    <DraggableMarker position={position} setPosition={setPosition} setLocation={setLocation} />
                </MapContainer>
            </div>


            {location.name && (
                <div style={styles.confirmationText}>
                    Selected Location: <strong>{location.name}</strong>
                </div>
            )}
        </div>
    );
};


const DateStep = ({ dates, setDates }) => {
    const today = new Date().toISOString().split('T')[0];
    const { mode = 'specific', startDate = '', endDate = '', period = 'first_week', month = 'jan' } = dates;
    
    const handleDateChange = (field, value) => {
        const newDates = { ...dates, [field]: value };
        if (field === 'startDate' && newDates.endDate && newDates.endDate < value) {
            newDates.endDate = value;
        }
        setDates(newDates);
    };

    const getConfirmationText = () => {
        if (mode === 'specific' && startDate && endDate) {
            return `From ${startDate} to ${endDate}`;
        }
        if (mode === 'general') {
            const periodText = {
                first_week: 'First week of',
                second_week: 'Second week of',
                first_2_weeks: 'First 2 weeks of',
                entire_month: 'Entire month of'
            }[period];
            const monthText = {
                jan: 'January', feb: 'February', mar: 'March', apr: 'April', may: 'May', jun: 'June', jul: 'July', aug: 'August', sep: 'September', oct: 'October', nov: 'November', dec: 'December'
            }[month];
            return `${periodText} ${monthText}`;
        }
        return 'Please select your dates';
    };

    return (
        <div style={styles.stepContainer}>
            <h2 style={styles.header}>🗓️ When are you going?</h2>
            <div style={styles.tabContainer}>
                <Tab label="Specific Range" isActive={mode === 'specific'} onClick={() => setDates({ ...dates, mode: 'specific' })} />
                <Tab label="General Period" isActive={mode === 'general'} onClick={() => setDates({ ...dates, mode: 'general' })} />
            </div>

            {mode === 'specific' && (
                <div style={styles.datePickerContainer}>
                    <div>
                        <label style={styles.label}>Start Date</label>
                        <input type="date" style={styles.dateInput} min={today} value={startDate} onChange={e => handleDateChange('startDate', e.target.value)} />
                    </div>
                    <div>
                        <label style={styles.label}>End Date</label>
                        <input type="date" style={styles.dateInput} min={startDate || today} value={endDate} onChange={e => handleDateChange('endDate', e.target.value)} />
                    </div>
                </div>
            )}

            {mode === 'general' && (
                 <div style={styles.datePickerContainer}>
                    <select style={styles.selectInput} value={period} onChange={e => handleDateChange('period', e.target.value)}>
                        <option value="first_week">First week of</option>
                        <option value="second_week">Second week of</option>
                        <option value="first_2_weeks">First 2 weeks of</option>
                        <option value="entire_month">Entire month of</option>
                    </select>
                    <select style={styles.selectInput} value={month} onChange={e => handleDateChange('month', e.target.value)}>
                        <option value="jan">January</option>
                        <option value="feb">February</option>
                        <option value="mar">March</option>
                        <option value="apr">April</option>
                        <option value="may">May</option>
                        <option value="jun">June</option>
                        <option value="jul">July</option>
                        <option value="aug">August</option>
                        <option value="sep">September</option>
                        <option value="oct">October</option>
                        <option value="nov">November</option>
                        <option value="dec">December</option>
                    </select>
                </div>
            )}
            <div style={styles.confirmationText}>
                Selected Dates: <strong>{getConfirmationText()}</strong>
            </div>
        </div>
    );
};

const ActivityStep = ({ profile, setProfile, profiles }) => {
    const { mode = 'choose', selectedProfileId = '', custom = {} } = profile;
    const { tempRange = [50, 70], precip = 'no_rain', wind = 30, clouds = 'clear', name = '' } = custom;
    
    const handleCustomChange = (field, value) => {
        let newCustom = { ...profile.custom, [field]: value };
        if (field === 'tempRangeMin') {
            const min = parseInt(value, 10) || 0;
            const max = tempRange[1];
            newCustom.tempRange = [min > max ? max : min, max];
        } else if (field === 'tempRangeMax') {
            const min = tempRange[0];
            const max = parseInt(value, 10) || 110;
            newCustom.tempRange = [min, max < min ? min : max];
        } else {
            newCustom[field] = value;
        }
        setProfile({ ...profile, custom: newCustom });
    };

    return (
        <div style={styles.stepContainer}>
            <h2 style={styles.header}>🧗 What are you planning?</h2>
            <div style={styles.tabContainer}>
                <Tab label="Choose a Profile" isActive={mode === 'choose'} onClick={() => setProfile({ ...profile, mode: 'choose' })} />
                <Tab label="Create a Custom Profile" isActive={mode === 'custom'} onClick={() => setProfile({ ...profile, mode: 'custom' })} />
            </div>

            {mode === 'choose' && (
                <div style={styles.profileGrid}>
                    {profiles.map(p => (
                        <div 
                            key={p.id} 
                            style={{
                                ...styles.profileCard,
                                ...(selectedProfileId === p.id ? styles.selectedProfileCard : {})
                            }}
                            onClick={() => setProfile({ ...profile, selectedProfileId: p.id })}
                        >
                            <div style={styles.profileIcon}>{p.icon}</div>
                            <div style={styles.profileName}>{p.name}</div>
                            {selectedProfileId === p.id && <div style={styles.profileDesc}>{p.desc}</div>}
                        </div>
                    ))}
                </div>
            )}
            {mode === 'custom' && (
                <div style={styles.customProfileForm}>
                    <div style={styles.formGroup}>
                        <label style={styles.label}>Ideal Temperature Range: {tempRange[0]}°F - {tempRange[1]}°F</label>
                         <div style={styles.sliderContainer}>
                            <input type="range" min="0" max="110" value={tempRange[0]} onChange={e => handleCustomChange('tempRangeMin', e.target.value)} style={{width: '100%'}}/>
                            <input type="range" min="0" max="110" value={tempRange[1]} onChange={e => handleCustomChange('tempRangeMax', e.target.value)} style={{width: '100%'}}/>
                         </div>
                    </div>
                    <div style={styles.formGroup}>
                        <label style={styles.label}>Precipitation</label>
                        <div style={styles.radioGroup}>
                           <label><input type="radio" name="precip" value="no_rain" checked={precip === 'no_rain'} onChange={e => handleCustomChange('precip', e.target.value)}/> No chances of rain!</label>
                           <label><input type="radio" name="precip" value="drizzle" checked={precip === 'drizzle'} onChange={e => handleCustomChange('precip', e.target.value)}/> A drizzle is okay.</label>
                           <label><input type="radio" name="precip" value="any" checked={precip === 'any'} onChange={e => handleCustomChange('precip', e.target.value)}/> Any conditions!</label>
                        </div>
                    </div>
                     <div style={styles.formGroup}>
                        <label style={styles.label}>Max Wind Speed: {wind} mph</label>
                         <input type="range" min="0" max="50" value={wind} onChange={e => handleCustomChange('wind', e.target.value)} style={{width: '100%'}}/>
                    </div>
                    <div style={styles.formGroup}>
                        <label style={styles.label}>Cloud Cover</label>
                         <div style={styles.radioGroup}>
                           <label><input type="radio" name="clouds" value="clear" checked={clouds === 'clear'} onChange={e => handleCustomChange('clouds', e.target.value)}/> Clear skies only</label>
                           <label><input type="radio" name="clouds" value="light" checked={clouds === 'light'} onChange={e => handleCustomChange('clouds', e.target.value)}/> Lightly Cloudy</label>
                           <label><input type="radio" name="clouds" value="cloudy" checked={clouds === 'cloudy'} onChange={e => handleCustomChange('clouds', e.target.value)}/> Cloudy</label>
                           <label><input type="radio" name="clouds" value="any" checked={clouds === 'any'} onChange={e => handleCustomChange('clouds', e.target.value)}/> Any conditions!</label>
                        </div>
                    </div>
                    <div style={styles.formGroup}>
                        <input type="text" style={styles.textInput} placeholder="Save as 'My Perfect Riverwalk Day'..." value={name} onChange={e => handleCustomChange('name', e.target.value)} />
                    </div>
                </div>
            )}
        </div>
    );
};


// --- Main App Component ---

function App() {
  const [currentStep, setCurrentStep] = useState(1);
  const [location, setLocation] = useState({ name: '', lat: null, lng: null });
  const [dates, setDates] = useState({ mode: 'specific', startDate: '', endDate: '' });
  const [activityProfile, setActivityProfile] = useState({ mode: 'choose', selectedProfileId: '' });
  
  // State for handling the analysis/report
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [reportData, setReportData] = useState(null);
  const [error, setError] = useState(null);
  
  // Define profiles here so they can be accessed by the backend function
  const profiles = [
        { id: 'beach', name: 'Lakefront Beach Day', icon: '🏖️', desc: 'Prefers warm, sunny, calm conditions.', params: { tempRange: [75, 90], precip: 'no_rain', wind: 15, clouds: 'clear' } },
        { id: 'trail', name: '606 Trail Walk/Bike', icon: '🚲', desc: 'Prefers mild, dry, and clear conditions.', params: { tempRange: [55, 75], precip: 'no_rain', wind: 20, clouds: 'any' } },
        { id: 'architecture', name: 'Architecture Tour', icon: '🏙️', desc: 'Prefers partly cloudy "soft light" and dry weather.', params: { tempRange: [60, 80], precip: 'no_rain', wind: 25, clouds: 'light' } },
        { id: 'festival', name: 'Street Festival', icon: '🎪', desc: 'Tolerant of crowds and heat, but not storms.', params: { tempRange: [65, 85], precip: 'drizzle', wind: 20, clouds: 'any' } },
        { id: 'cubs_game', name: 'Cubs Game Day', icon: '⚾', desc: 'Ideal for a warm afternoon, no rain delays!', params: { tempRange: [68, 82], precip: 'no_rain', wind: 20, clouds: 'light' } },
    ];


  const isStepComplete = useMemo(() => {
    if (currentStep === 1) return !!location.name;
    if (currentStep === 2) return (dates.mode === 'specific' && dates.startDate && dates.endDate) || (dates.mode === 'general');
    if (currentStep === 3) return (activityProfile.mode === 'choose' && activityProfile.selectedProfileId) || (activityProfile.mode === 'custom' && activityProfile.custom.name);
    return false;
  }, [currentStep, location, dates, activityProfile]);

  const handleNext = () => {
      if (isStepComplete) {
          setCurrentStep(prev => Math.min(prev + 1, 4));
      }
  };
  const handleBack = () => {
    if (currentStep === 4) {
        setReportData(null);
        setError(null);
        setIsAnalyzing(false);
    }
    setCurrentStep(prev => Math.max(prev - 1, 1));
  };
  
  // --- BACKEND INTEGRATION FUNCTION ---
  const handleGenerateReport = async () => {
    setIsAnalyzing(true);
    setError(null);
    setReportData(null);

    let profileData;
    if (activityProfile.mode === 'choose') {
        const selected = profiles.find(p => p.id === activityProfile.selectedProfileId);
        profileData = selected ? selected.params : {};
    } else {
        profileData = activityProfile.custom;
    }

    const requestBody = {
        location: {
            latitude: location.lat,
            longitude: location.lng,
        },
        dates: dates,
        profile: profileData
    };

    try {
        console.log("Sending to backend:", JSON.stringify(requestBody, null, 2));

        const response = await fetch('/api/climatology-report', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestBody),
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        await new Promise(resolve => setTimeout(resolve, 1500)); 
        const mockData = {
            suitabilityScore: 82,
            summary: "Historically, this is an excellent time for a Lakefront Beach Day.",
            temperature: {
                average: "75°F",
                chanceInIdealRange: "88%"
            },
            precipitation: {
                chanceOfRain: "15%"
            }
        };
        setReportData(mockData);

    } catch (e) {
        console.error("Failed to fetch report:", e);
        setError("Sorry, we couldn't generate the report. Please try again later.");
        setReportData(null);
    } finally {
        setIsAnalyzing(false);
    }
  };
    
  return (
    <div style={styles.appContainer}>
      <div style={styles.plannerWrapper}>
        <h1 style={styles.title}>Chicago Event Planner</h1>
        <Stepper currentStep={currentStep} />
        
        <div style={styles.contentArea}>
            {currentStep === 1 && <LocationStep location={location} setLocation={setLocation} />}
            {currentStep === 2 && <DateStep dates={dates} setDates={setDates} />}
            {currentStep === 3 && <ActivityStep profile={activityProfile} setProfile={setActivityProfile} profiles={profiles} />}
            {currentStep === 4 && (
                <div style={styles.stepContainer}>
                    {isAnalyzing && (
                        <div>
                            <h2 style={styles.header}>Analyzing Climate Data...</h2>
                            <p>Querying decades of NASA satellite data for your specific request. This may take a moment.</p>
                            <div style={styles.spinner}></div>
                        </div>
                    )}
                    {error && (
                         <div>
                            <h2 style={{...styles.header, color: '#dc3545'}}>Analysis Failed</h2>
                            <p style={styles.errorText}>{error}</p>
                         </div>
                    )}
                    {reportData && (
                        <div>
                            <h2 style={{...styles.header, color: '#28a745'}}>Analysis Complete!</h2>
                            <div style={styles.summaryBox}>
                                <h3>Suitability Score: {reportData.suitabilityScore}%</h3>
                                <p>{reportData.summary}</p>
                                <ul>
                                    <li>Avg Temp: {reportData.temperature.average}</li>
                                    <li>Chance of Rain: {reportData.precipitation.chanceOfRain}</li>
                                </ul>
                            </div>
                        </div>
                    )}
                    {!isAnalyzing && !reportData && !error && (
                        <div>
                            <h2 style={styles.header}>✅ Ready to Analyze!</h2>
                            <button onClick={handleGenerateReport} style={styles.analyzeButtonFinal}>
                                Generate Climatology Report
                            </button>
                        </div>
                    )}
                </div>
            )}
        </div>

        <div style={styles.navigation}>
          {currentStep > 1 && <button style={styles.backButton} onClick={handleBack}>Back</button>}
          {currentStep < 4 ? (
             <button style={{...styles.nextButton, ...(!isStepComplete ? styles.disabledButton : {})}} onClick={handleNext} disabled={!isStepComplete}>Next</button>
          ) : null}
        </div>
      </div>
    </div>
  );
}

// --- Styles ---
const styles = {
    appContainer: { fontFamily: "'Segoe UI', Roboto, sans-serif", backgroundColor: '#f0f4f8', minHeight: '100vh', display: 'flex', justifyContent: 'center', alignItems: 'center', padding: '20px' },
    plannerWrapper: { backgroundColor: '#ffffff', borderRadius: '16px', boxShadow: '0 8px 30px rgba(0,0,0,0.1)', width: '100%', maxWidth: '700px', overflow: 'hidden' },
    title: { textAlign: 'center', color: '#1e2a3b', padding: '20px 0', margin: 0, borderBottom: '1px solid #e9ecef' },
    stepperContainer: { display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', padding: '20px 40px' },
    stepWrapper: { display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center', width: '80px' },
    stepCircle: { width: '30px', height: '30px', borderRadius: '50%', display: 'flex', justifyContent: 'center', alignItems: 'center', fontWeight: 'bold', transition: 'background-color 0.3s' },
    stepLabel: { marginTop: '8px', fontSize: '14px', fontWeight: '500', transition: 'color 0.3s' },
    stepConnector: { flex: 1, height: '2px', backgroundColor: '#e9ecef', margin: '15px -20px 0 -20px' },
    contentArea: { padding: '20px 40px', minHeight: '400px' },
    stepContainer: { display: 'flex', flexDirection: 'column', gap: '20px' },
    header: { color: '#1e2a3b', margin: '0 0 10px 0', fontSize: '24px', textAlign: 'center' },
    navigation: { display: 'flex', justifyContent: 'space-between', padding: '20px 40px', borderTop: '1px solid #e9ecef' },
    nextButton: { backgroundColor: '#007bff', color: '#fff', border: 'none', padding: '12px 25px', borderRadius: '8px', cursor: 'pointer', fontSize: '16px', fontWeight: 'bold', transition: 'background-color 0.2s' },
    backButton: { backgroundColor: '#6c757d', color: '#fff', border: 'none', padding: '12px 25px', borderRadius: '8px', cursor: 'pointer', fontSize: '16px' },
    disabledButton: { backgroundColor: '#ced4da', cursor: 'not-allowed' },
    // Location Step
    locationControls: { display: 'flex', gap: '10px', alignItems: 'center' },
    inputGroup: { position: 'relative' },
    searchInput: { width: '100%', boxSizing: 'border-box', padding: '12px', fontSize: '16px', border: '1px solid #ced4da', borderRadius: '8px' },
    locationButton: { padding: '10px', border: '1px solid #ced4da', borderRadius: '8px', backgroundColor: '#fff', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center' },
    autocompleteDropdown: { position: 'absolute', width: '100%', backgroundColor: 'white', border: '1px solid #ced4da', borderRadius: '8px', marginTop: '5px', boxShadow: '0 4px 15px rgba(0,0,0,0.1)', zIndex: 1000, boxSizing: 'border-box' },
    autocompleteItem: { padding: '12px', cursor: 'pointer', borderBottom: '1px solid #f0f4f8' },
    mapContainer: { height: '200px', borderRadius: '8px', overflow: 'hidden', zIndex: 1 },
    confirmationText: { marginTop: '15px', color: '#28a745', fontWeight: 'bold', fontSize: '16px', textAlign: 'center', backgroundColor: '#e9f7ef', padding: '10px', borderRadius: '8px' },
    // Tabs
    tabContainer: { display: 'flex', borderBottom: '1px solid #ced4da', marginBottom: '20px' },
    tab: { padding: '10px 15px', border: 'none', backgroundColor: 'transparent', cursor: 'pointer', fontSize: '16px', color: '#6c757d', borderBottom: '3px solid transparent' },
    activeTab: { color: '#007bff', fontWeight: 'bold', borderBottom: '3px solid #007bff' },
    // Date Step
    datePickerContainer: { display: 'flex', gap: '20px', justifyContent: 'center', flexWrap: 'wrap' },
    label: { display: 'block', marginBottom: '5px', color: '#495057', fontSize: '14px' },
    dateInput: { padding: '10px', fontSize: '16px', border: '1px solid #ced4da', borderRadius: '8px' },
    selectInput: { padding: '10px', fontSize: '16px', border: '1px solid #ced4da', borderRadius: '8px', flex: 1, minWidth: '180px' },
    // Activity Step
    profileGrid: { display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))', gap: '15px' },
    profileCard: { borderWidth: '2px', borderStyle: 'solid', borderColor: '#ced4da', borderRadius: '12px', padding: '15px', textAlign: 'center', cursor: 'pointer', transition: 'all 0.2s ease-in-out' },
    selectedProfileCard: { borderColor: '#007bff', backgroundColor: '#f0f8ff', transform: 'scale(1.05)', boxShadow: '0 4px 15px rgba(0,0,0,0.1)' },
    profileIcon: { fontSize: '36px' },
    profileName: { fontWeight: 'bold', marginTop: '10px' },
    profileDesc: { fontSize: '12px', color: '#6c757d', marginTop: '5px' },
    customProfileForm: { display: 'flex', flexDirection: 'column', gap: '20px' },
    formGroup: { display: 'flex', flexDirection: 'column', gap: '8px' },
    sliderContainer: { display: 'flex', flexDirection: 'column', gap: '10px' },
    radioGroup: { display: 'flex', gap: '15px', flexWrap: 'wrap' },
    textInput: { padding: '12px', fontSize: '16px', border: '1px solid #ced4da', borderRadius: '8px' },
    // Summary & Report
    summaryBox: { backgroundColor: '#f8f9fa', border: '1px solid #e9ecef', borderRadius: '8px', padding: '20px' },
    analyzeButtonFinal: { width: '100%', backgroundColor: '#28a745', color: '#fff', border: 'none', padding: '15px', borderRadius: '8px', cursor: 'pointer', fontSize: '18px', fontWeight: 'bold', marginTop: '20px' },
    errorText: { color: '#dc3545', textAlign: 'center' },
    spinner: {
        margin: '20px auto',
        border: '4px solid #f3f3f3',
        borderTop: '4px solid #3498db',
        borderRadius: '50%',
        width: '40px',
        height: '40px',
        animation: 'spin 1s linear infinite'
    },
    // Keyframes for spinner animation
    '@keyframes spin': {
        '0%': { transform: 'rotate(0deg)' },
        '100%': { transform: 'rotate(360deg)' }
    }
};

// Add keyframes to the document's head
const styleSheet = document.createElement("style");
styleSheet.type = "text/css";
styleSheet.innerText = `
@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}`;
document.head.appendChild(styleSheet);


ReactDOM.render(<App />, document.getElementById('root'));