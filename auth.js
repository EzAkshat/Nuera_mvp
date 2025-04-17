const passport = require('passport');
const GoogleStrategy = require('passport-google-oauth20').Strategy;
const fs = require('fs');
const path = require('path');

passport.use(new GoogleStrategy({
    clientID: 'YOUR_GOOGLE_CLIENT_ID',
    clientSecret: 'YOUR_GOOGLE_CLIENT_SECRET',
    callbackURL: 'http://localhost:3000/auth/google/callback'
  },
  (accessToken, refreshToken, profile, done) => {
    const userData = {
      name: profile.displayName,
      email: profile.emails[0].value
    };
    fs.writeFileSync(path.join(__dirname, 'user.json'), JSON.stringify(userData));
    return done(null, profile);
  }
));

passport.serializeUser((user, done) => done(null, user));
passport.deserializeUser((user, done) => done(null, user));

module.exports = passport;