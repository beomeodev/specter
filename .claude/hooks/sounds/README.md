# Sound Files for Task Notifications

This directory contains audio files for task completion notifications.

## Required Files

1. **task-complete.mp3** - Plays when Write/Edit tools complete
2. **input-needed.mp3** - Plays when user input is required

## Specifications

- **Format**: MP3
- **Duration**: 0.5 - 1.5 seconds
- **Size**: < 50KB recommended
- **Bit Rate**: 128kbps, Mono, 44.1kHz

## Where to Get Sounds

### Free Sources

- [Notification Sounds](https://notificationsounds.com/) - Free notification sound library
- [Freesound](https://freesound.org/) - Creative Commons sound library
- [Zapsplat](https://www.zapsplat.com/) - Free sound effects

### Recommended Sounds

**task-complete.mp3**:
- Search for: "success", "complete", "done", "positive notification"
- Tone: Subtle, pleasant, non-intrusive

**input-needed.mp3**:
- Search for: "question", "attention", "prompt", "gentle notification"
- Tone: Soft, questioning, inviting

## Installation

1. Download your preferred notification sounds
2. Rename them to:
   - `task-complete.mp3`
   - `input-needed.mp3`
3. Place them in this directory
4. The hooks will automatically use them

## Platform Support

Currently supports:
- **Windows/WSL**: Uses PowerShell Media.SoundPlayer

## Disable Notifications

To disable sound notifications:
- Simply delete the sound files from this directory
- The hooks will silently skip playback if files don't exist

## Testing

Test the sounds manually:

### Windows/WSL:
```powershell
powershell.exe -c "(New-Object Media.SoundPlayer 'task-complete.mp3').PlaySync();"
```

### Linux (if applicable):
```bash
mpg123 task-complete.mp3
```
