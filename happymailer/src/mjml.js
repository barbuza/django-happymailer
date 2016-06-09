import { defineMode, getMode, overlayMode } from 'codemirror';

defineMode('mjml', function(config) {
  const htmlBase = getMode(config, 'xml');
  const djangoInner = getMode(config, 'django:inner');
  return overlayMode(htmlBase, djangoInner);
});
