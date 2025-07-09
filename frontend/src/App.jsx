import React, { useState, useEffect, useRef } from 'react';

// --- THEME CONFIGURATION (REFINED) ---
const THEMES = {
  neon: {
    id: 'neon',
    name: 'Neon Wave',
    backgroundImage: '/bd4.webp',
    colors: {
      primary: 'fuchsia',
      secondary: 'cyan',
      text: 'text-white',
      textMuted: 'text-gray-300',
      dialogue1: 'text-fuchsia-400',
      dialogue2: 'text-cyan-400',
    }
  },
  golden: {
    id: 'golden',
    name: 'Golden Hour',
    backgroundImage: '/bd2.webp',
    colors: {
      primary: 'amber',
      secondary: 'sky',
      text: 'text-white',
      textMuted: 'text-gray-300',
      dialogue1: 'text-amber-300',
      dialogue2: 'text-sky-300',
    }
  },
  pastel: {
    id: 'pastel',
    name: 'Pastel Dreams',
    backgroundImage: '/bd3.webp',
    colors: {
      primary: 'violet',
      secondary: 'emerald',
      text: 'text-white',
      textMuted: 'text-gray-300',
      dialogue1: 'text-violet-400',
      dialogue2: 'text-emerald-400',
    }
  },
  bubblegum: {
    id: 'bubblegum',
    name: 'Bubblegum',
    backgroundImage: '/bd1.webp',
    colors: {
      primary: 'rose',
      secondary: 'sky',
      text: 'text-white',
      textMuted: 'text-gray-300',
      dialogue1: 'text-rose-400',
      dialogue2: 'text-sky-400',
    }
  }
};


// --- Helper Components & Data ---

// A simple heuristic to guess gender from first name for avatar selection
const getGender = (name) => {
  const maleNames = ['Brian', 'Steffan', 'Adam', 'Andrew', 'Davis', 'Dustin'];
  const firstName = name.split(' ')[0];
  return maleNames.includes(firstName) ? 'male' : 'female';
};

// SVG Icons
const ICONS = {
  appLogo: "M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3ZM19 10v2a7 7 0 0 1-14 0v-2M5 18a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1",
  url: "M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.72",
  pdf: "M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8zM6 22V4h7v5h5v13H6z",
  podcast: "M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3ZM19 10v2a7 7 0 0 1-14 0v-2M12 19v3",
  restart: "M12 5V1L7 6l5 5V7c3.31 0 6 2.69 6 6s-2.69 6-6 6-6-2.69-6-6H4c0 4.42 3.58 8 8 8s8-3.58 8-8-3.58-8-8-8z",
  plus: "M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z",
  error: "M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z",
  close: "M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z",
  male: "M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z",
  female: "M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v1h16v-1c0-2.66-5.33-4-8-4z",
  arrowLeft: "M15.41 7.41L14 6l-6 6 6 6 1.41-1.41L10.83 12z",
};

const Icon = ({ path, className = "w-6 h-6", isAppLogo = false }) => (
  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill={isAppLogo ? 'none' : 'currentColor'} stroke={isAppLogo ? 'currentColor' : 'none'} strokeWidth={isAppLogo ? 1.5 : 0} className={className}>
    {isAppLogo ? (
        <>
            <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z" fill="#f9a8d4" stroke="none"/>
            <path d="M19 10v2a7 7 0 0 1-14 0v-2" strokeLinecap="round"/>
            <path d="M5 18a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1" strokeLinecap="round"/>
        </>
    ) : (
        <path d={path} />
    )}
  </svg>
);

const ALL_SPEAKERS = [
  'Ava Smith', 'Brian Stark', 'Steffan Johnson', 'Adam Brown', 'Andrew White',
  'Amanda Turner', 'Emma Clark', 'Nancy Roberts', 'Natasha Cook', 'Davis Hall', 'Dustin'
].map(name => ({ name, gender: getGender(name) }));

// --- Animated Background Component ---
const AnimatedBackground = ({ theme }) => (
    <>
        <style>{`
            @keyframes fade-in { from { opacity: 0; } to { opacity: 1; } }
            .fade-in { animation: fade-in 0.8s ease-out forwards; }
            @keyframes fade-in-up { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
            .fade-in-up { animation: fade-in-up 0.6s ease-out forwards; }
        `}</style>
        <div 
            className="absolute top-0 left-0 w-full h-full bg-cover bg-center z-0 transition-all duration-700"
            style={{ backgroundImage: `url(${theme.backgroundImage})` }}
        ></div>
        {/* Diffused Overlay - Increased opacity for better contrast */}
        <div className="absolute top-0 left-0 w-full h-full bg-black/70 z-0"></div>
    </>
);

const ProgressDots = ({ total, current }) => (
    <div className="flex justify-center gap-3">
        {Array.from({ length: total }).map((_, i) => (
            <div key={i} className={`w-3 h-3 rounded-full transition-all duration-300 ${i + 1 === current ? 'bg-white scale-125' : 'bg-white/30'}`}></div>
        ))}
    </div>
);


// --- Child Components for Pages ---

const HomePage = ({
  loading, error, handleSubmit, inputType, setInputType, sourceUrl, setSourceUrl,
  fileData, handleFileChange, speakers, removeSpeaker, setIsSpeakerModalOpen,
  podcastLength, setPodcastLength, theme
}) => {
    const [step, setStep] = useState(1);
    const nextStep = () => setStep(s => s + 1);
    const prevStep = () => setStep(s => s - 1);

    const renderStep = () => {
        const stepContentKey = `step-${step}`;
        const primaryColor = theme.colors.primary;
        const secondaryColor = theme.colors.secondary;
        const baseBg = 'bg-white/5';
        const hoverBg = 'bg-white/10';
        
        switch(step) {
            case 1: return (
                <div key={stepContentKey} className="text-center fade-in-up">
                    <h2 className={`text-3xl md:text-4xl font-bold ${theme.colors.text} mb-8`}>How do you want to start?</h2>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <button type="button" onClick={() => { setInputType('url'); nextStep(); }} className={`p-8 ${baseBg} border-2 border-transparent rounded-2xl text-left hover:border-${primaryColor}-400 hover:${hoverBg} transition-all group`}>
                            <Icon path={ICONS.url} className={`w-12 h-12 text-${primaryColor}-500 mb-4`} />
                            <h3 className={`text-2xl font-bold ${theme.colors.text}`}>From a URL</h3>
                            <p className={`${theme.colors.textMuted} mt-2`}>Paste a link to any online article.</p>
                        </button>
                        <button type="button" onClick={() => { setInputType('pdf'); nextStep(); }} className={`p-8 ${baseBg} border-2 border-transparent rounded-2xl text-left hover:border-${secondaryColor}-400 hover:${hoverBg} transition-all group`}>
                            <Icon path={ICONS.pdf} className={`w-12 h-12 text-${secondaryColor}-500 mb-4`} />
                            <h3 className={`text-2xl font-bold ${theme.colors.text}`}>From a PDF</h3>
                            <p className={`${theme.colors.textMuted} mt-2`}>Upload a document from your device.</p>
                        </button>
                    </div>
                </div>
            );
            case 2: return (
                <div key={stepContentKey} className="text-center fade-in-up">
                    <h2 className={`text-3xl md:text-4xl font-bold ${theme.colors.text} mb-8`}>
                        {inputType === 'url' ? 'Paste the article URL' : 'Upload your PDF'}
                    </h2>
                    {inputType === 'url' ? (
                        <input type="url" value={sourceUrl} onChange={(e) => setSourceUrl(e.target.value)} placeholder="https://..." className={`w-full max-w-xl mx-auto ${baseBg} ${theme.colors.text} text-center text-lg placeholder-gray-400 p-4 rounded-xl border-2 border-gray-700 focus:border-${primaryColor}-400 focus:ring-1 focus:ring-${primaryColor}-400 transition-all`}/>
                    ) : (
                        <label className={`w-full max-w-xl mx-auto flex flex-col items-center justify-center ${baseBg} ${theme.colors.textMuted} p-12 rounded-xl border-2 border-dashed border-gray-600 cursor-pointer hover:${hoverBg} hover:border-${secondaryColor}-400 transition-all`}>
                            <Icon path={ICONS.pdf} className={`w-16 h-16 mb-4 text-${secondaryColor}-500`} />
                            <span className={`font-semibold ${theme.colors.text}`}>{fileData.name || 'Click or drag to upload'}</span>
                            <input type="file" accept=".pdf" onChange={handleFileChange} className="hidden" />
                        </label>
                    )}
                </div>
            );
            case 3:
                const SpeakerTag = ({ speaker, onRemove }) => (
                    <div className="flex items-center gap-2 bg-black/20 rounded-full p-1 pr-3 text-white transition-all hover:bg-black/40">
                        <div className={`w-10 h-10 rounded-full flex items-center justify-center ${speaker.gender === 'male' ? `bg-${secondaryColor}-500/70` : `bg-${primaryColor}-500/70`}`}>
                            <Icon path={ICONS[speaker.gender]} className="w-6 h-6" />
                        </div>
                        <span className="font-bold">{speaker.name}</span>
                        <button type="button" onClick={() => onRemove(speaker.name)} className="ml-2 text-gray-400 hover:text-white">
                            <Icon path={ICONS.close} className="w-5 h-5" />
                        </button>
                    </div>
                );
                return (
                    <div key={stepContentKey} className="text-center fade-in-up">
                        <h2 className={`text-3xl md:text-4xl font-bold ${theme.colors.text} mb-8`}>Assemble your cast</h2>
                        <div className="flex flex-wrap items-center justify-center gap-4 max-w-2xl mx-auto">
                            {speakers.map(speaker => <SpeakerTag key={speaker.name} speaker={speaker} onRemove={removeSpeaker} />)}
                            {speakers.length < 5 && (
                                <button type="button" onClick={() => setIsSpeakerModalOpen(true)} className="w-12 h-12 flex items-center justify-center bg-white/10 rounded-full text-white hover:bg-white/20 transition-all transform hover:scale-110">
                                    <Icon path={ICONS.plus} className="w-8 h-8" />
                                </button>
                            )}
                        </div>
                    </div>
                );
            case 4: return (
                <div key={stepContentKey} className="text-center fade-in-up">
                    <h2 className={`text-3xl md:text-4xl font-bold ${theme.colors.text} mb-8`}>And finally, the length...</h2>
                    <div className="flex justify-center gap-4 mb-12">
                        {['short', 'moderate', 'long'].map(len => (
                            <button key={len} type="button" onClick={() => setPodcastLength(len)} className={`px-8 py-4 text-lg font-bold rounded-xl transition-all duration-300 capitalize border-2 ${podcastLength === len ? `bg-white/20 border-white/50 ${theme.colors.text}` : `bg-white/5 border-transparent ${theme.colors.textMuted} hover:bg-white/10`}`}>{len}</button>
                        ))}
                    </div>
                    <button type="button" onClick={handleSubmit} className={`w-full max-w-xs mx-auto flex items-center justify-center gap-3 bg-gradient-to-r from-${secondaryColor}-500 to-${primaryColor}-600 text-white font-bold py-4 rounded-xl shadow-lg shadow-black/20 hover:from-${secondaryColor}-600 hover:to-${primaryColor}-700 transition-all duration-300 disabled:from-gray-500 disabled:to-gray-600 disabled:cursor-not-allowed transform hover:scale-105`} disabled={loading}>
                        <Icon path={ICONS.podcast} className="w-6 h-6" />
                        <span>{loading ? "Generating..." : "Generate Podcast"}</span>
                    </button>
                </div>
            );
            default: return null;
        }
    };

    const isNextDisabled = () => {
        if (step === 2) {
            if (inputType === 'url' && !sourceUrl) return true;
            if (inputType === 'pdf' && !fileData.content) return true;
        }
        return false;
    };

    return (
        <div className="w-full max-w-4xl mx-auto flex flex-col items-center justify-center">
            <div className="w-full min-h-[400px] flex items-center justify-center">
                {renderStep()}
            </div>
            
            <div className="mt-12 w-full flex items-center justify-between">
                <button type="button" onClick={prevStep} disabled={step === 1} className="px-6 py-2 text-white/50 hover:text-white disabled:opacity-0 transition-all">Back</button>
                <ProgressDots total={4} current={step} />
                {step < 4 ? (
                    <button type="button" onClick={nextStep} disabled={isNextDisabled()} className="px-6 py-2 bg-white/10 text-white rounded-lg hover:bg-white/20 disabled:opacity-50 disabled:cursor-not-allowed transition-all">Next</button>
                ) : (
                    <div className="w-[76px]"></div> // Placeholder for alignment
                )}
            </div>
            {loading && (
                <div className="mt-8 text-center fade-in-up">
                    <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-teal-400"></div>
                    <p className="mt-4 text-gray-300">Brewing your podcast... this may take a moment.</p>
                </div>
            )}
            {error && (
                <div className="mt-8 mx-auto max-w-2xl bg-red-500/20 border border-red-500 text-red-300 px-4 py-3 rounded-xl flex items-center gap-3 fade-in-up">
                    <Icon path={ICONS.error} className="w-8 h-8"/>
                    <span><strong>Error:</strong> {error}</span>
                </div>
            )}
        </div>
    );
};

const ResultPage = ({ result, handleRestart, theme }) => {
  const parseScript = (script) => {
    const elements = [];
    const lines = script.split('\n').filter(line => line.trim() !== '');

    lines.forEach(line => {
      const speakerMatch = line.match(/^\*\*(.*?):\*\*\s*(.*)/);
      if (speakerMatch) {
        elements.push({ type: 'dialogue', speaker: speakerMatch[1], text: speakerMatch[2] });
        return;
      }
      
      const segmentMatch = line.match(/^Segment\s*\d+:\s*(.*)/i);
      if (segmentMatch) {
        elements.push({ type: 'segment', text: segmentMatch[1] });
        return;
      }

      if (line.trim()) {
         elements.push({ type: 'title', text: line });
      }
    });
    return elements;
  };

  const scriptElements = parseScript(result.podcast_script);

  return (
    <div className="w-full h-full flex flex-col fade-in">
      <main className="w-full flex-grow overflow-y-auto pt-24 pb-32">
        <div className="max-w-3xl mx-auto p-8 md:p-12 space-y-8">
          {scriptElements.map((el, index) => {
            if (el.type === 'segment') {
              return (
                <h2 key={index} className={`text-4xl md:text-5xl font-bold text-center ${theme.colors.text} pt-8 pb-4`}>
                  {el.text}
                </h2>
              );
            }
            if (el.type === 'dialogue') {
              const speakerInfo = ALL_SPEAKERS.find(s => s.name === el.speaker) || { gender: 'male' };
              const speakerColor = speakerInfo.gender === 'male' ? theme.colors.dialogue2 : theme.colors.dialogue1;
              return (
                <div key={index} className="grid grid-cols-1 md:grid-cols-[150px_1fr] gap-x-6 gap-y-2">
                  <div className={`flex items-center gap-2 justify-end md:border-r ${theme.colors.text === 'text-white' ? 'border-white/20' : 'border-slate-300'} pr-6 ${speakerColor}`}>
                    <span className="font-bold text-right">{el.speaker}</span>
                    <Icon path={ICONS[speakerInfo.gender]} className="w-5 h-5" />
                  </div>
                  <p className={`${theme.colors.textMuted} text-lg leading-relaxed`}>{el.text}</p>
                </div>
              );
            }
            return null;
          })}
        </div>
      </main>

      <footer className={`fixed bottom-0 left-0 right-0 p-4 ${theme.colors.text === 'text-white' ? 'bg-black/20' : 'bg-white/20'} backdrop-blur-lg border-t ${theme.colors.text === 'text-white' ? 'border-white/10' : 'border-black/10'}`}>
        <div className="max-w-3xl mx-auto">
          <audio controls src={`data:audio/mpeg;base64,${result.audio_data}`} className="w-full audio-player"></audio>
        </div>
      </footer>
    </div>
  );
};


// --- Main App Component (Router) ---

export default function App() {
  const [activeTheme, setActiveTheme] = useState(THEMES.neon);
  const [inputType, setInputType] = useState('url');
  const [sourceUrl, setSourceUrl] = useState('');
  const [fileData, setFileData] = useState({ name: '', content: '' });
  const [speakers, setSpeakers] = useState([ALL_SPEAKERS[0], ALL_SPEAKERS[1]]);
  const [podcastLength, setPodcastLength] = useState('moderate');
  const [isSpeakerModalOpen, setIsSpeakerModalOpen] = useState(false);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    if (file.type !== "application/pdf") {
      setError("Please upload a valid PDF file.");
      setFileData({ name: '', content: '' });
      return;
    }
    const reader = new FileReader();
    reader.onload = (event) => {
      const base64Content = event.target.result.split(',')[1];
      setFileData({ name: file.name, content: base64Content });
      setError(null);
    };
    reader.onerror = () => setError("Failed to read the file.");
    reader.readAsDataURL(file);
  };
  
  const addSpeaker = (speaker) => {
    if (speakers.length < 5 && !speakers.find(s => s.name === speaker.name)) {
      setSpeakers([...speakers, speaker]);
    }
    setIsSpeakerModalOpen(false);
  };

  const removeSpeaker = (speakerNameToRemove) => {
    if (speakers.length > 1) {
      setSpeakers(speakers.filter(s => s.name !== speakerNameToRemove));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if ((inputType === 'url' && !sourceUrl) || (inputType === 'pdf' && !fileData.content)) {
      setError("Please provide a source URL or a PDF file.");
      return;
    }
    setError(null);
    setLoading(true);
    setResult(null);

    const speakerPayload = {};
    speakers.forEach((speaker, index) => {
      speakerPayload[`speaker${index + 1}`] = speaker.name;
    });

    const payload = {
      file: inputType === 'pdf' ? fileData.content : null,
      url: inputType === 'url' ? sourceUrl : null,
      no_of_speaker: speakers.length,
      speaker: speakerPayload,
      podcast_length: podcastLength,
    };

    try {
      const response = await fetch("http://127.0.0.1:8000/podcasts/", {
        method: "POST",
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      const responseData = await response.json();
      if (!response.ok) throw new Error(responseData.detail || `HTTP error! status: ${response.status}`);
      setResult(responseData.data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleRestart = () => {
    setResult(null);
    setError(null);
    setSourceUrl('');
    setFileData({ name: '', content: '' });
    setInputType('url');
    setSpeakers([ALL_SPEAKERS[0], ALL_SPEAKERS[1]]);
    setPodcastLength('moderate');
  };

  const SpeakerSelectionModal = ({ isOpen, onClose, onSelect, currentSpeakers }) => {
    if (!isOpen) return null;
    const availableSpeakers = ALL_SPEAKERS.filter(s => !currentSpeakers.find(cs => cs.name === s.name));
    return (
      <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 fade-in" style={{animationDuration: '0.3s'}}>
        <div className="bg-gray-800/80 border border-white/20 rounded-2xl shadow-2xl w-full max-w-md p-6" onClick={e => e.stopPropagation()}>
          <h3 className="text-xl font-bold text-white mb-4">Select a Speaker</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 max-h-80 overflow-y-auto">
            {availableSpeakers.map(speaker => (
              <button key={speaker.name} type="button" onClick={() => onSelect(speaker)} className="flex items-center gap-3 p-3 rounded-lg text-left bg-white/5 hover:bg-teal-500/50 transition-all">
                <div className={`w-10 h-10 rounded-full flex items-center justify-center ${speaker.gender === 'male' ? `bg-${activeTheme.colors.secondary}-500/70` : `bg-${activeTheme.colors.primary}-500/70`}`}>
                  <Icon path={ICONS[speaker.gender]} className="w-6 h-6 text-white" />
                </div>
                <span className="font-semibold text-white">{speaker.name}</span>
              </button>
            ))}
          </div>
        </div>
      </div>
    );
  };
  
  const ThemeSwitcher = () => (
    <div className="flex items-center gap-2 bg-black/20 p-1 rounded-full">
        {Object.values(THEMES).map(theme => (
            <button 
                key={theme.id}
                onClick={() => setActiveTheme(theme)}
                className={`w-8 h-8 rounded-full bg-cover bg-center border-2 transition-all ${activeTheme.id === theme.id ? 'border-white' : 'border-transparent opacity-50 hover:opacity-100'}`}
                style={{backgroundImage: `url(${theme.backgroundImage})`}}
                title={`Switch to ${theme.name} theme`}
            ></button>
        ))}
    </div>
  );

  return (
    <div className={`h-screen w-screen bg-black ${activeTheme.colors.text} font-sans flex flex-col overflow-hidden relative`}>
      <AnimatedBackground theme={activeTheme} />
      
      {/* This header is now conditional and only shows on the result page */}
      {result && (
        <header className="fixed top-0 left-0 w-full p-4 z-30 bg-black/20 backdrop-blur-lg border-b border-white/10">
            <div className="max-w-5xl mx-auto flex items-center justify-between gap-4">
              <button onClick={handleRestart} className="flex items-center gap-2 text-gray-300 hover:text-white transition-colors flex-shrink-0">
                <Icon path={ICONS.arrowLeft} className="w-6 h-6" />
                <span className="font-semibold hidden sm:inline">Create New</span>
              </button>
              <h1 className="text-lg font-bold text-center text-gray-200 truncate min-w-0 flex-grow">
                {result.title}
              </h1>
              <div className="w-24 flex-shrink-0"></div> {/* Placeholder to balance the header */}
            </div>
        </header>
      )}

      {/* This header is for the main page */}
      {!result && (
        <header className="absolute top-0 left-0 w-full p-4 z-20 flex justify-between items-center">
            <div className="flex items-center gap-3">
                <Icon path={ICONS.appLogo} className="w-10 h-10 text-white" isAppLogo={true} />
                <span className="font-bold text-xl text-white hidden sm:inline">AI Podcast Studio</span>
            </div>
            <ThemeSwitcher />
        </header>
      )}
      
      <main className="relative z-10 w-full h-full flex items-center justify-center p-4">
        {!result ? (
            <HomePage
              loading={loading}
              error={error}
              handleSubmit={handleSubmit}
              inputType={inputType}
              setInputType={setInputType}
              sourceUrl={sourceUrl}
              setSourceUrl={setSourceUrl}
              fileData={fileData}
              handleFileChange={handleFileChange}
              speakers={speakers}
              removeSpeaker={removeSpeaker}
              setIsSpeakerModalOpen={setIsSpeakerModalOpen}
              podcastLength={podcastLength}
              setPodcastLength={setPodcastLength}
              theme={activeTheme}
            />
        ) : (
          <ResultPage result={result} handleRestart={handleRestart} theme={activeTheme} />
        )}
      </main>
      
      <footer className="absolute bottom-0 right-0 p-4 z-20">
        <a href="https://github.com/aijuggler" target="_blank" rel="noopener noreferrer" className="text-sm text-gray-400 hover:text-white transition-colors">
            Made with ❤️ by Ankita Tiwari
        </a>
      </footer>

      <SpeakerSelectionModal 
        isOpen={isSpeakerModalOpen} 
        onClose={() => setIsSpeakerModalOpen(false)}
        onSelect={addSpeaker}
        currentSpeakers={speakers}
      />
    </div>
  );
}
