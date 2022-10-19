
export default function Menu() {

  function run() {
    alert("Not ready yet");
  }

  return (
    <nav className="navbar is-info" role="navigation" aria-label="main navigation">
      <div className="navbar-brand">
        <a className="navbar-item" href="/">
          <img src={`${process.env.PUBLIC_URL}/ai.png` } alt="Icon of a robot from https://www.flaticon.com/"/>
          <h1> CSIA-PME</h1>
        </a>
      </div>
      <div className="navbar-menu">
        <div className="navbar-end">
          <div className="navbar-item">
              {/*<button className="button is-info is-light" onClick={() => run()}>Run</button>*/}
          </div>
        </div>
      </div>
    </nav>
  );
}

