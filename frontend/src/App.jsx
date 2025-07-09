import React, { useState, useEffect, useRef } from 'react';

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
  upload: "M9.99988 15.1709L19.1923 5.97852L20.6065 7.39273L9.99988 17.9993L3.63588 11.6354L5.04988 10.2212L9.99988 15.1709Z",
  podcast: "M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3ZM19 10v2a7 7 0 0 1-14 0v-2M12 19v3",
  restart: "M12 5V1L7 6l5 5V7c3.31 0 6 2.69 6 6s-2.69 6-6 6-6-2.69-6-6H4c0 4.42 3.58 8 8 8s8-3.58 8-8-3.58-8-8-8z",
  plus: "M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z",
  error: "M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z",
  close: "M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z",
  male: "M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z",
  female: "M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v1h16v-1c0-2.66-5.33-4-8-4z",
  arrowLeft: "M15.41 7.41L14 6l-6 6 6 6 1.41-1.41L10.83 12z"
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
const AnimatedBackground = () => (
    <>
        <style>{`
            @keyframes animate-gradient {
                0% { background-position: 0% 50%; }
                50% { background-position: 100% 50%; }
                100% { background-position: 0% 50%; }
            }
            .gradient-bg {
                background: linear-gradient(-45deg, #0f0c29, #302b63, #24243e, #1a2a6c, #b21f1f, #fdbb2d);
                background-size: 400% 400%;
                animation: animate-gradient 25s ease infinite;
            }
            @keyframes fade-in-up {
                from { opacity: 0; transform: translateY(20px); }
                to { opacity: 1; transform: translateY(0); }
            }
            .fade-in-up {
                animation: fade-in-up 0.6s ease-out forwards;
            }
        `}</style>
        <div className="absolute top-0 left-0 w-full h-full gradient-bg z-0"></div>
        <div className="absolute top-0 left-0 w-full h-full bg-black/30 z-0"></div>
    </>
);


// --- Child Components for Pages ---

const HomePage = ({
  loading, error, handleSubmit, inputType, setInputType, sourceUrl, setSourceUrl,
  fileData, handleFileChange, speakers, removeSpeaker, setIsSpeakerModalOpen,
  podcastLength, setPodcastLength
}) => {
    const SpeakerTag = ({ speaker, onRemove }) => (
    <div className="flex items-center gap-2 bg-gray-700/50 rounded-full p-1 pr-2 text-white transition-all hover:bg-gray-600/50 hover:shadow-lg hover:shadow-fuchsia-500/20">
      <div className={`w-8 h-8 rounded-full flex items-center justify-center ${speaker.gender === 'male' ? 'bg-teal-500/70' : 'bg-fuchsia-500/70'}`}>
        <Icon path={ICONS[speaker.gender]} className="w-5 h-5" />
      </div>
      <span className="font-medium text-sm">{speaker.name}</span>
      <button type="button" onClick={() => onRemove(speaker.name)} className="text-gray-400 hover:text-white">
        <Icon path={ICONS.close} className="w-4 h-4" />
      </button>
    </div>
  );

  return (
    <div className="w-full max-w-2xl mx-auto fade-in-up">
      <div className="bg-gray-900/50 backdrop-blur-xl p-8 rounded-2xl shadow-2xl shadow-black/30 border border-gray-700">
        <h1 className="text-4xl md:text-5xl font-bold text-white text-center bg-clip-text text-transparent bg-gradient-to-r from-teal-300 to-fuchsia-400">
          AI Podcast Studio
        </h1>
        <p className="text-gray-300 mt-2 text-center text-lg">
          Transform articles and documents into engaging podcasts.
        </p>

        <form onSubmit={handleSubmit} className="mt-8 space-y-6">
          <div className="grid grid-cols-2 gap-2 bg-gray-800/80 p-1 rounded-xl">
            <button type="button" onClick={() => setInputType('url')} className={`px-4 py-2 text-sm font-semibold rounded-lg transition-all duration-300 ${inputType === 'url' ? 'bg-teal-500/80 text-white shadow-lg shadow-teal-500/30' : 'text-gray-300 hover:bg-gray-700/50'}`}>From URL</button>
            <button type="button" onClick={() => setInputType('pdf')} className={`px-4 py-2 text-sm font-semibold rounded-lg transition-all duration-300 ${inputType === 'pdf' ? 'bg-fuchsia-500/80 text-white shadow-lg shadow-fuchsia-500/30' : 'text-gray-300 hover:bg-gray-700/50'}`}>From PDF</button>
          </div>

          <div>
            {inputType === 'url' ? (
              <input type="url" value={sourceUrl} onChange={(e) => setSourceUrl(e.target.value)} placeholder="https://example.com/article" className="w-full bg-gray-800/80 text-white placeholder-gray-400 p-4 rounded-xl border-2 border-gray-700 focus:border-teal-400 focus:ring-1 focus:ring-teal-400 transition-all"/>
            ) : (
              <label className="w-full flex items-center justify-center bg-gray-800/80 text-gray-300 p-4 rounded-xl border-2 border-dashed border-gray-600 cursor-pointer hover:bg-gray-700/50 hover:border-fuchsia-400 transition-all">
                <Icon path={ICONS.upload} className="w-6 h-6 mr-3 text-fuchsia-400" />
                <span>{fileData.name || 'Click to upload a PDF file'}</span>
                <input type="file" accept=".pdf" onChange={handleFileChange} className="hidden" />
              </label>
            )}
          </div>
          
          <div className="bg-gray-800/80 p-4 rounded-xl border-2 border-gray-700">
             <label className="text-gray-300 font-semibold mb-3 block">Podcast Speakers</label>
             <div className="flex flex-wrap items-center gap-2">
                {speakers.map(speaker => (
                    <SpeakerTag key={speaker.name} speaker={speaker} onRemove={removeSpeaker} />
                ))}
                {speakers.length < 5 && (
                    <button type="button" onClick={() => setIsSpeakerModalOpen(true)} className="w-10 h-10 flex items-center justify-center bg-gray-700/80 rounded-full text-teal-300 hover:bg-teal-500/50 hover:text-white transition-all transform hover:scale-110">
                        <Icon path={ICONS.plus} className="w-6 h-6" />
                    </button>
                )}
             </div>
          </div>

          <div className="flex items-center justify-between bg-gray-800/80 p-2 rounded-xl border-2 border-gray-700">
            <label className="text-gray-300 font-semibold pl-2">Podcast Length</label>
            <div className="flex items-center gap-1 bg-gray-900/50 p-1 rounded-lg">
                {['short', 'moderate', 'long'].map(len => (
                    <button key={len} type="button" onClick={() => setPodcastLength(len)} className={`px-4 py-1.5 text-sm font-semibold rounded-md transition-all duration-300 capitalize ${podcastLength === len ? 'bg-teal-500/80 text-white shadow-md shadow-teal-500/20' : 'text-gray-300 hover:bg-gray-700/50'}`}>{len}</button>
                ))}
            </div>
          </div>

          <button type="submit" className="w-full flex items-center justify-center gap-3 bg-gradient-to-r from-teal-500 to-fuchsia-600 text-white font-bold py-4 rounded-xl shadow-lg shadow-black/20 hover:from-teal-600 hover:to-fuchsia-700 transition-all duration-300 disabled:from-gray-500 disabled:to-gray-600 disabled:cursor-not-allowed transform hover:scale-105" disabled={loading}>
            <Icon path={ICONS.podcast} className="w-6 h-6" />
            <span>{loading ? "Generating Your Podcast..." : "Generate Podcast"}</span>
          </button>
        </form>
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

const ResultPage = ({ result, handleRestart }) => {
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
    <div className="w-full h-full flex flex-col fade-in-up">
      <header className="w-full p-4 flex-shrink-0 bg-gray-900/50 backdrop-blur-lg border-b border-gray-700/50">
        <div className="max-w-5xl mx-auto flex items-center justify-between">
          <button onClick={handleRestart} className="flex items-center gap-2 text-gray-300 hover:text-white transition-colors">
            <Icon path={ICONS.arrowLeft} className="w-6 h-6" />
            <span className="font-semibold">Create New Podcast</span>
          </button>
          <h1 className="text-lg font-bold text-center text-gray-200 truncate px-4">
            {result.title}
          </h1>
        </div>
      </header>

      <main className="w-full flex-grow overflow-y-auto pb-32">
        <div className="max-w-3xl mx-auto p-8 md:p-12 space-y-8">
          {scriptElements.map((el, index) => {
            if (el.type === 'segment') {
              return (
                <h2 key={index} className="text-4xl md:text-5xl font-bold text-center text-white pt-8 pb-4">
                  {el.text}
                </h2>
              );
            }
            if (el.type === 'dialogue') {
              const speakerInfo = ALL_SPEAKERS.find(s => s.name === el.speaker) || { gender: 'male' };
              const speakerColor = speakerInfo.gender === 'male' ? 'text-teal-300' : 'text-fuchsia-300';
              return (
                <div key={index} className="grid grid-cols-1 md:grid-cols-[150px_1fr] gap-x-6 gap-y-2">
                  <div className={`flex items-center gap-2 justify-end md:border-r border-gray-700 pr-6 ${speakerColor}`}>
                    <span className="font-bold text-right">{el.speaker}</span>
                    <Icon path={ICONS[speakerInfo.gender]} className="w-5 h-5" />
                  </div>
                  <p className="text-gray-300 text-lg leading-relaxed">{el.text}</p>
                </div>
              );
            }
            return null;
          })}
        </div>
      </main>

      <footer className="fixed bottom-0 left-0 right-0 p-4 bg-gray-900/50 backdrop-blur-lg border-t border-gray-700/50">
        <div className="max-w-3xl mx-auto">
          <audio controls src={`data:audio/mpeg;base64,${result.audio_data}`} className="w-full audio-player"></audio>
        </div>
      </footer>
    </div>
  );
};


// --- Main App Component (Router) ---

export default function App() {
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
      <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 fade-in-up" style={{animationDuration: '0.3s'}}>
        <div className="bg-gray-800 border border-gray-700 rounded-2xl shadow-2xl w-full max-w-md p-6" onClick={e => e.stopPropagation()}>
          <h3 className="text-xl font-bold text-white mb-4">Select a Speaker</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 max-h-80 overflow-y-auto">
            {availableSpeakers.map(speaker => (
              <button key={speaker.name} onClick={() => onSelect(speaker)} className="flex items-center gap-3 p-3 rounded-lg text-left bg-gray-700/50 hover:bg-teal-500/50 transition-all">
                <div className={`w-10 h-10 rounded-full flex items-center justify-center ${speaker.gender === 'male' ? 'bg-teal-500/70' : 'bg-fuchsia-500/70'}`}>
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

  return (
    <div className="h-screen w-screen bg-black text-white font-sans flex flex-col overflow-hidden relative">
      <AnimatedBackground />
      
      <header className="absolute top-0 left-0 p-4 z-20">
        <div className="flex items-center gap-3">
            <Icon path={ICONS.appLogo} className="w-10 h-10 text-white" isAppLogo={true} />
            <span className="font-bold text-xl text-white">AI Podcast Studio</span>
        </div>
      </header>
      
      <div className="relative z-10 w-full h-full flex items-center justify-center p-4">
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
          />
        ) : (
          <ResultPage result={result} handleRestart={handleRestart} />
        )}
      </div>
      
      <footer className="absolute bottom-0 right-0 p-4 z-20">
        <p className="text-sm text-gray-400">Made with ❤️ by <a href="https://github.com/aijuggler" target="_blank" rel="noopener noreferrer" className="text-teal-400 hover:underline">Ankita Tiwari</a></p>
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
