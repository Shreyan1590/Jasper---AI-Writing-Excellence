export default function AppBar() {
    return (
        <header className="app-bar">
            <div className="app-bar-brand">
                <div className="app-bar-logo">J</div>
                <span>Jasper</span>
            </div>

            <div className="app-bar-search">
                <div className="search-input">
                    <span className="search-icon">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                            <circle cx="11" cy="11" r="8" />
                            <line x1="21" y1="21" x2="16.65" y2="16.65" />
                        </svg>
                    </span>
                    <input
                        className="input"
                        type="text"
                        placeholder="Search..."
                        aria-label="Search"
                    />
                </div>
            </div>

            <div className="app-bar-actions">
                <button className="btn btn-ghost btn-sm" aria-label="Notifications">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" />
                        <path d="M13.73 21a2 2 0 0 1-3.46 0" />
                    </svg>
                </button>

                <button className="btn btn-ghost btn-sm" aria-label="User menu">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
                        <circle cx="12" cy="7" r="4" />
                    </svg>
                </button>
            </div>
        </header>
    );
}
