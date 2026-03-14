import { MdNotifications, MdSearch, MdPerson } from 'react-icons/md';
import { FaGithub } from 'react-icons/fa';

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
                        <MdSearch size={20} />
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
                <a 
                    href="https://github.com" 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="btn btn-ghost btn-sm"
                    aria-label="GitHub Repository"
                >
                    <FaGithub size={20} />
                </a>

                <button className="btn btn-ghost btn-sm" aria-label="Notifications">
                    <MdNotifications size={20} />
                </button>

                <button className="btn btn-ghost btn-sm" aria-label="User menu">
                    <MdPerson size={20} />
                </button>
            </div>
        </header>
    );
}
