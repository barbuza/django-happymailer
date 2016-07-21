import React from 'react';
import { render } from 'react-dom';
import 'whatwg-fetch';
import './staticUrl';
import App from './App';

render(
  <App { ...window.happymailerConfig }/>,
  document.getElementById('react-app')
);
