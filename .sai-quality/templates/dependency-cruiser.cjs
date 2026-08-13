module.exports = {
  forbidden: [
    { name: 'no-circular', severity: 'error', from: {}, to: { circular: true } },
    { name: 'not-to-unresolvable', severity: 'error', from: {}, to: { couldNotResolve: true } },
    { name: 'no-orphans', severity: 'warn', from: { orphan: true }, to: {} }
  ],
  options: { doNotFollow: { path: 'node_modules' } }
};
