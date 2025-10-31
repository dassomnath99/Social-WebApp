# Chat + Social App 🚀

A full-stack real-time social media platform that seamlessly combines traditional social networking features with instant messaging capabilities. Built with modern web technologies to deliver a responsive, real-time user experience.

## 🎯 Overview

This application provides a comprehensive social networking experience with integrated real-time chat functionality, allowing users to connect, share, and communicate instantly on a single platform.

## 🛠️ Tech Stack

- **Backend Framework:** Django 4.x
- **Real-time Communication:** Django Channels, WebSockets
- **Message Broker:** Redis
- **Authentication:** JWT (JSON Web Tokens)
- **Design Philosophy:** Mobile-first, responsive UI

## ✨ Features

### 💬 Real-time Chat
- **WebSocket-powered messaging** for instant communication
- **Typing indicators** to show when others are composing messages
- **Read receipts** to track message delivery and reading status
- **Online status tracking** to see who's currently active
- **Persistent message history** for conversation continuity
- **File and image sharing** within chat conversations

### 👥 Social Networking
- **Follow system** to connect with other users
- **Personalized news feeds** tailored to your connections
- **Post interactions** including likes and comments
- **Custom user profiles** with personalized information
- **Content sharing** with image and file upload support

### 🔐 Security
- **JWT-based authentication** for secure, stateless sessions
- Token-based API access control
- Secure WebSocket connections

### 📱 User Experience
- **Responsive design** optimized for all devices
- **Mobile-first approach** ensuring great performance on smartphones
- Intuitive interface for seamless navigation

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- Redis Server
- pip (Python package manager)
- Virtual environment (recommended)

### Installation

1. **Clone the repository**
```bash
   git clone <repository-url>
   cd chat-social-app
```

2. **Create and activate virtual environment**
```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
   pip install -r requirements.txt
```

4. **Configure environment variables**
```bash
   cp .env.example .env
   # Edit .env with your configuration
```

5. **Start Redis server**
```bash
   redis-server
```

6. **Run database migrations**
```bash
   python manage.py migrate
```

7. **Create a superuser (optional)**
```bash
   python manage.py createsuperuser
```

8. **Start the development server**
```bash
   python manage.py runserver
```

9. **In a separate terminal, start the Channels worker** (if needed)
```bash
   python manage.py runworker
```

The application should now be running at `http://localhost:8000`

## 📁 Project Structure
```
chat-social-app/
├── apps/
│   ├── chat/              # Real-time chat functionality
│   ├── social/            # Social networking features
│   └── users/             # User authentication and profiles
├── config/                # Django settings and configuration
├── static/                # Static files (CSS, JS, images)
├── media/                 # User-uploaded content
├── templates/             # HTML templates
└── manage.py
```

## 🔧 Configuration

### Redis Configuration

Update your `settings.py` with Redis connection details:
```python
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('127.0.0.1', 6379)],
        },
    },
}
```

### JWT Configuration

Configure JWT settings in `settings.py`:
```python
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    # Additional JWT settings...
}
```

## 📚 API Documentation

The application provides RESTful API endpoints for:
- User authentication (login, register, token refresh)
- Profile management
- Social feed operations
- Post creation and interactions
- Real-time chat via WebSocket connections

## 🧪 Testing

Run the test suite:
```bash
python manage.py test
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Django and Django Channels communities
- Contributors and testers
- Open-source libraries and tools used in this project

## 📧 Contact

For questions or support, please open an issue in the repository or contact the maintainers.

---

**Built with ❤️ using Django and WebSockets**