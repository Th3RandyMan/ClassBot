# Username Filtering System - User Guide

## Overview

The ClassBot now includes a comprehensive username filtering system that automatically detects inappropriate usernames and takes configurable actions. This system is designed for academic environments to maintain a professional atmosphere.

## Features

### 🔍 **Detection Capabilities**
- **Basic Profanity Detection**: Catches direct inappropriate words
- **Compound Word Detection**: Finds profanity within longer usernames (e.g., "fuckthisclass")
- **L33t Speak Detection**: Identifies character substitutions (f@ck, n1gg3r, etc.)
- **Spacing Evasion**: Detects spaced letters (f u c k)
- **Character Repetition**: Catches extended letters (fuuuuck, shiiiit)
- **Backwards Words**: Identifies reversed inappropriate terms (kcuf)
- **Context-Aware**: Configurable sensitivity levels

### ⚙️ **Configuration Options**
- **Sensitivity Levels**: Low, Medium, High
- **Action Types**: None, Warn, Kick, Ban
- **Custom Word Lists**: Profanity, Hate Speech, Inappropriate content
- **Whitelist System**: Exempt specific usernames from filtering
- **Pattern Controls**: Enable/disable specific detection methods

## Commands

### 🔧 **Admin Commands**

#### `!check_usernames [action]`
**Permission Required**: Admin/TA roles only

Scans all server members for inappropriate usernames.

**Usage Examples:**
```
!check_usernames report          # Generate report only
!check_usernames warn            # Send warning DMs to flagged users
!check_usernames kick            # Kick users with high-confidence violations
!check_usernames stats           # Show filter statistics
```

**Output:**
- Total members scanned
- Number of flagged users
- Top violations with confidence scores
- Actions taken (if any)

#### `!username_whitelist [action] [username]`
**Permission Required**: Admin/TA roles only

Manage the username whitelist for exempt users.

**Usage Examples:**
```
!username_whitelist add @StudentName     # Add user to whitelist
!username_whitelist remove @StudentName  # Remove from whitelist  
!username_whitelist list                 # Show all whitelisted users
```

## Automatic Detection

### 🚨 **New Member Screening**
When new members join the server:

1. **Automatic Scan**: Both username and display name are checked
2. **Confidence Scoring**: System calculates violation confidence (0.0-1.0)
3. **Configurable Actions**: Based on settings in `config/username_filter.json`
4. **Admin Notifications**: Alerts sent to mod/admin channels
5. **User Communication**: Automatic DMs with policy reminders

### 📊 **Detection Examples**

#### ✅ **Clean Usernames** (Won't be flagged)
- `normaluser123`
- `ClassTA_Helper`
- `study_group_leader`
- `johnsmith2024`
- `mathtutor`

#### 🚩 **Inappropriate Usernames** (Will be flagged)
- `fuckthisclass` (Direct profanity in compound word)
- `xxxporn123` (Explicit content)
- `nazipower` (Hate speech)
- `f u c k` (Spacing evasion)
- `fuuuuck` (Character repetition)
- `kcuf` (Backwards profanity)

## Configuration

### 📝 **Config File Location**
`config/username_filter.json`

### 🎛️ **Key Settings**

```json
{
  "enabled": true,
  "sensitivity": "medium",
  "action_on_detection": "warn",
  "word_lists": {
    "profanity": ["word1", "word2", ...],
    "hate_speech": ["term1", "term2", ...],
    "inappropriate": ["content1", "content2", ...]
  },
  "patterns": {
    "character_replacement": true,
    "spacing_evasion": true,
    "repeat_characters": true,
    "backwards_words": true
  }
}
```

#### **Sensitivity Levels:**
- **Low**: Only catches severe violations (hate speech)
- **Medium**: Standard filtering (recommended for academic use)
- **High**: Aggressive filtering (may have more false positives)

#### **Action Types:**
- **none**: Detection only, no automatic action
- **warn**: Send DM warning to user
- **kick**: Remove user from server (high confidence only)
- **ban**: Permanently ban user (reserved for severe cases)

## Best Practices

### 👍 **Recommended Settings**
- **Sensitivity**: Medium (balanced accuracy)
- **Action**: Warn (educational approach)
- **Review Period**: Check detection logs weekly
- **Whitelist**: Add false positives to prevent re-flagging

### ⚠️ **Important Considerations**
1. **False Positives**: May occur with legitimate names (use whitelist)
2. **Cultural Sensitivity**: Some words may be inappropriate in academic context but acceptable elsewhere
3. **Regular Review**: Monitor detection accuracy and adjust as needed
4. **Privacy**: System logs detections for admin review only

## Troubleshooting

### 🔧 **Common Issues**

#### **Filter Too Aggressive**
- Lower sensitivity to "low"
- Add false positives to whitelist
- Disable specific pattern types

#### **Filter Too Permissive**
- Increase sensitivity to "high"
- Add custom words to filter lists
- Enable all pattern detection methods

#### **Performance Issues**
- Reduce word list sizes
- Disable complex patterns (l33t speak, backwards)
- Consider batch processing for large servers

### 📞 **Support**
For technical issues or configuration help, contact your system administrator.

## Privacy & Ethics

### 🛡️ **Data Protection**
- Usernames are processed locally only
- No external API calls or data sharing
- Detection logs stored securely on server
- Configurable data retention policies

### ⚖️ **Fair Use**
- Transparent detection process
- User notifications before actions
- Appeal process through admin team
- Consistent application of policies

---

**System Version**: 1.0  
**Last Updated**: September 25, 2025  
**Compatible with**: Discord.py 2.3.2+