# MP3Yap - Modern Futuristic Design System

## Design Vision

**Konsept:** Cyberpunk / Neo-Dystopian / Futuristic
**Atmosfer:** Karanlık, neon vurgulu, teknolojik, vurucu
**İlham:** Blade Runner, Cyberpunk 2077, Tron Legacy, Ghost in the Shell

---

## 1. Color Palette

### Primary - Neon Accent Colors

| Renk | Hex | RGB | Kullanım |
|------|-----|-----|----------|
| Electric Purple | `#711C91` | 113, 28, 145 | Primary accent |
| Hot Pink | `#EA00D9` | 234, 0, 217 | CTA buttons, highlights |
| Neon Cyan | `#0ABDC6` | 10, 189, 198 | Secondary accent, links |
| Electric Blue | `#6300FF` | 99, 0, 255 | Hover states, active |

### Background - Dark Tones

| Renk | Hex | RGB | Kullanım |
|------|-----|-----|----------|
| Deep Space | `#0A0A0F` | 10, 10, 15 | Main background |
| Dark Navy | `#091833` | 9, 24, 51 | Card backgrounds |
| Midnight Purple | `#1A0A2E` | 26, 10, 46 | Secondary surfaces |
| Charcoal | `#1B1B2A` | 27, 27, 42 | Elevated surfaces |

### Accent - Glow Colors

| Renk | Hex | RGB | Kullanım |
|------|-----|-----|----------|
| Neon Pink Glow | `#FF007A` | 255, 0, 122 | Error, warnings, glow |
| Cyber Yellow | `#F9C54E` | 249, 197, 78 | Progress, success alt |
| Matrix Green | `#00FFB3` | 0, 255, 179 | Success states |
| Ice Blue | `#00BFFF` | 0, 191, 255 | Info, loading |

### Gradient Presets

```dart
// Cyberpunk Gradient (primary)
LinearGradient(
  colors: [Color(0xFF711C91), Color(0xFFEA00D9), Color(0xFF0ABDC6)],
  begin: Alignment.topLeft,
  end: Alignment.bottomRight,
)

// Dark Fade (backgrounds)
LinearGradient(
  colors: [Color(0xFF0A0A0F), Color(0xFF1A0A2E)],
  begin: Alignment.topCenter,
  end: Alignment.bottomCenter,
)

// Neon Glow (buttons)
LinearGradient(
  colors: [Color(0xFFEA00D9), Color(0xFF6300FF)],
  begin: Alignment.centerLeft,
  end: Alignment.centerRight,
)
```

---

## 2. Typography

### Font Önerileri

| Kategori | Font | Alternatif | Kullanım |
|----------|------|------------|----------|
| Display | **Orbitron** | Audiowide | Başlıklar, logo |
| Headings | **Rajdhani** | Exo 2 | Section headers |
| Body | **Inter** | Roboto | Genel metin |
| Mono | **JetBrains Mono** | Fira Code | Dosya yolları, kodlar |

### Font Sizes (Scale)

```dart
// Display
displayLarge: 48px / bold / letterSpacing: 2
displayMedium: 36px / bold / letterSpacing: 1.5

// Headlines
headlineLarge: 28px / semibold
headlineMedium: 24px / semibold
headlineSmall: 20px / semibold

// Body
bodyLarge: 16px / regular
bodyMedium: 14px / regular
bodySmall: 12px / regular

// Labels
labelLarge: 14px / medium
labelMedium: 12px / medium
labelSmall: 10px / medium / uppercase / letterSpacing: 1.5
```

---

## 3. UI Components

### 3.1 Glassmorphism Cards

```dart
Container(
  decoration: BoxDecoration(
    gradient: LinearGradient(
      colors: [
        Colors.white.withOpacity(0.1),
        Colors.white.withOpacity(0.05),
      ],
      begin: Alignment.topLeft,
      end: Alignment.bottomRight,
    ),
    borderRadius: BorderRadius.circular(16),
    border: Border.all(
      color: Colors.white.withOpacity(0.2),
      width: 1,
    ),
    boxShadow: [
      BoxShadow(
        color: Color(0xFFEA00D9).withOpacity(0.1),
        blurRadius: 20,
        spreadRadius: -5,
      ),
    ],
  ),
  child: ClipRRect(
    borderRadius: BorderRadius.circular(16),
    child: BackdropFilter(
      filter: ImageFilter.blur(sigmaX: 10, sigmaY: 10),
      child: // content
    ),
  ),
)
```

### 3.2 Neon Glow Buttons

```dart
Container(
  decoration: BoxDecoration(
    gradient: LinearGradient(
      colors: [Color(0xFFEA00D9), Color(0xFF6300FF)],
    ),
    borderRadius: BorderRadius.circular(12),
    boxShadow: [
      BoxShadow(
        color: Color(0xFFEA00D9).withOpacity(0.5),
        blurRadius: 20,
        spreadRadius: 0,
      ),
      BoxShadow(
        color: Color(0xFF6300FF).withOpacity(0.3),
        blurRadius: 40,
        spreadRadius: 0,
      ),
    ],
  ),
)
```

### 3.3 Input Fields (Cyber Style)

```dart
TextField(
  decoration: InputDecoration(
    filled: true,
    fillColor: Color(0xFF1B1B2A),
    border: OutlineInputBorder(
      borderRadius: BorderRadius.circular(8),
      borderSide: BorderSide(color: Color(0xFF0ABDC6).withOpacity(0.3)),
    ),
    focusedBorder: OutlineInputBorder(
      borderRadius: BorderRadius.circular(8),
      borderSide: BorderSide(color: Color(0xFF0ABDC6), width: 2),
    ),
    prefixIcon: Icon(Icons.search, color: Color(0xFF0ABDC6)),
  ),
)
```

### 3.4 Progress Indicators

```dart
// Neon Progress Bar
LinearProgressIndicator(
  value: progress,
  backgroundColor: Color(0xFF1B1B2A),
  valueColor: AlwaysStoppedAnimation<Color>(Color(0xFFEA00D9)),
)

// Animated Glow Effect
AnimatedContainer(
  decoration: BoxDecoration(
    boxShadow: [
      BoxShadow(
        color: Color(0xFFEA00D9).withOpacity(isActive ? 0.6 : 0.2),
        blurRadius: isActive ? 20 : 10,
      ),
    ],
  ),
)
```

---

## 4. Background Animations

### 4.1 Particle Network

```yaml
# pubspec.yaml
dependencies:
  particles_flutter: ^0.1.4
  # veya
  particles_network: ^1.0.0
```

```dart
ParticleNetworkWidget(
  particleCount: 50,
  particleColor: Color(0xFF0ABDC6),
  lineColor: Color(0xFFEA00D9).withOpacity(0.3),
  particleSize: 3,
  lineWidth: 1,
  maxDistance: 150,
)
```

### 4.2 Animated Gradient Background

```dart
class AnimatedGradientBackground extends StatefulWidget {
  @override
  _AnimatedGradientBackgroundState createState() => _AnimatedGradientBackgroundState();
}

class _AnimatedGradientBackgroundState extends State<AnimatedGradientBackground>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;

  final List<Color> colorList = [
    Color(0xFF0A0A0F),
    Color(0xFF1A0A2E),
    Color(0xFF091833),
    Color(0xFF711C91).withOpacity(0.3),
  ];

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: Duration(seconds: 10),
    )..repeat(reverse: true);
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _controller,
      builder: (context, child) {
        return Container(
          decoration: BoxDecoration(
            gradient: LinearGradient(
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
              colors: colorList,
              stops: [
                0.0,
                0.3 + (_controller.value * 0.2),
                0.6 + (_controller.value * 0.1),
                1.0,
              ],
            ),
          ),
        );
      },
    );
  }
}
```

### 4.3 Scan Lines Effect (Retro CRT)

```dart
CustomPaint(
  painter: ScanLinesPainter(
    lineSpacing: 4,
    lineOpacity: 0.05,
  ),
)

class ScanLinesPainter extends CustomPainter {
  final double lineSpacing;
  final double lineOpacity;

  ScanLinesPainter({this.lineSpacing = 4, this.lineOpacity = 0.05});

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = Colors.black.withOpacity(lineOpacity)
      ..strokeWidth = 1;

    for (double y = 0; y < size.height; y += lineSpacing) {
      canvas.drawLine(Offset(0, y), Offset(size.width, y), paint);
    }
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}
```

### 4.4 Grid Pattern (Tron Style)

```dart
CustomPaint(
  painter: GridPatternPainter(
    gridSize: 40,
    lineColor: Color(0xFF0ABDC6).withOpacity(0.1),
    glowColor: Color(0xFF0ABDC6).withOpacity(0.05),
  ),
)
```

### 4.5 Floating Orbs / Bokeh Effect

```dart
class FloatingOrb {
  Offset position;
  double size;
  Color color;
  double speed;
  double opacity;
}

// Rastgele konumlanmış, yavaşça hareket eden neon toplar
// Blur ile soft glow efekti
```

---

## 5. Animations & Micro-interactions

### 5.1 Page Transitions

```dart
// Fade + Scale
PageRouteBuilder(
  pageBuilder: (context, animation, secondaryAnimation) => page,
  transitionsBuilder: (context, animation, secondaryAnimation, child) {
    return FadeTransition(
      opacity: animation,
      child: ScaleTransition(
        scale: Tween<double>(begin: 0.95, end: 1.0).animate(
          CurvedAnimation(parent: animation, curve: Curves.easeOutCubic),
        ),
        child: child,
      ),
    );
  },
)
```

### 5.2 Button Hover Effects

- Scale: 1.0 → 1.05
- Glow intensity: 0.3 → 0.6
- Duration: 200ms
- Curve: easeOutCubic

### 5.3 Card Hover Effects

- Translate Y: 0 → -4px
- Border glow: 0.2 → 0.5 opacity
- Shadow blur: 10 → 20
- Duration: 300ms

### 5.4 Loading States

```dart
// Pulsing glow animation
AnimatedContainer(
  duration: Duration(milliseconds: 1500),
  decoration: BoxDecoration(
    boxShadow: [
      BoxShadow(
        color: Color(0xFFEA00D9).withOpacity(isPulsing ? 0.6 : 0.2),
        blurRadius: isPulsing ? 30 : 10,
      ),
    ],
  ),
)
```

---

## 6. Icons & Imagery

### Icon Style

- **Çizgi kalınlığı:** 1.5px - 2px
- **Köşeler:** Rounded
- **Renk:** Neon accent (context'e göre)
- **Boyut:** 20px (small), 24px (default), 32px (large)

### Recommended Icon Sets

1. **Phosphor Icons** - Modern, consistent
2. **Feather Icons** - Clean, minimal
3. **Remix Icons** - Comprehensive

### Custom Glow Icons

```dart
ShaderMask(
  shaderCallback: (bounds) => LinearGradient(
    colors: [Color(0xFFEA00D9), Color(0xFF0ABDC6)],
  ).createShader(bounds),
  child: Icon(Icons.music_note, color: Colors.white),
)
```

---

## 7. Spacing & Layout

### Spacing Scale

```dart
const spacing = {
  'xs': 4.0,
  'sm': 8.0,
  'md': 16.0,
  'lg': 24.0,
  'xl': 32.0,
  'xxl': 48.0,
};
```

### Border Radius

```dart
const radius = {
  'sm': 4.0,
  'md': 8.0,
  'lg': 12.0,
  'xl': 16.0,
  'xxl': 24.0,
  'full': 9999.0,
};
```

---

## 8. Implementation Packages

### Required Dependencies

```yaml
dependencies:
  # Blur & Glass Effects
  glassmorphism: ^3.0.0
  blur: ^3.1.0

  # Animations
  flutter_animate: ^4.2.0
  simple_animations: ^5.0.2

  # Particles & Effects
  particles_flutter: ^0.1.4
  animated_background: ^2.0.0

  # Gradients
  gradient_borders: ^1.0.0

  # Custom Fonts
  google_fonts: ^6.1.0
```

---

## 9. Component Hierarchy

```
App
├── AnimatedGradientBackground
│   └── ParticleOverlay (optional)
├── ScanLinesOverlay (subtle)
├── MainContent
│   ├── GlassAppBar
│   ├── GlassCards
│   │   └── NeonBorders
│   └── NeonButtons
└── AnimatedNavBar (glow effects)
```

---

## 10. Dark/Light Mode

**Not:** Bu tasarım sistemi **sadece dark mode** için optimize edilmiştir. Light mode kullanılmayacak veya minimal olacak.

Dark mode özellikleri:
- Deep backgrounds (#0A0A0F - #1B1B2A)
- High contrast neon accents
- Subtle glow effects
- Reduced eye strain

---

## 11. Performance Considerations

### ⚠️ GPU-Intensive Elements

| Element | Risk Level | Mitigation |
|---------|------------|------------|
| BackdropFilter (blur) | HIGH | Limit to small areas, use ClipRRect |
| Particle animations | MEDIUM | Reduce count on older devices |
| BoxShadow with blur | MEDIUM | Use cached shadows, avoid stacking |
| Animated gradients | LOW | Keep animations subtle |

### Performance Mode Setting

```dart
// Settings'e eklenecek
class PerformanceMode {
  static const full = 'full';        // Tüm efektler açık
  static const balanced = 'balanced'; // Blur kapalı, particles azaltılmış
  static const minimal = 'minimal';   // Animasyonlar kapalı, düz renkler
}

// Conditional rendering
if (performanceMode != PerformanceMode.minimal) {
  return GlassmorphicCard(...);
} else {
  return SimpleCard(...); // Blur olmadan, solid color
}
```

### Blur Alternatives (Low Performance)

```dart
// BackdropFilter yerine Opacity ile simülasyon
Container(
  decoration: BoxDecoration(
    color: Color(0xFF1B1B2A).withOpacity(0.95),
    borderRadius: BorderRadius.circular(16),
  ),
)
```

---

## 12. Accessibility Guidelines

### Font Usage Rules

| Context | Font | Why |
|---------|------|-----|
| App logo, splash | Orbitron | Brand identity |
| Section headers only | Orbitron/Rajdhani | Visual hierarchy |
| Body text, lists | Inter | Readability |
| File paths, URLs | JetBrains Mono | Clarity |
| Buttons, labels | Inter Medium | Balance |

### Contrast Requirements

- Body text: minimum 4.5:1 contrast ratio
- Large text (18px+): minimum 3:1 contrast ratio
- Interactive elements: clear focus indicators

### Neon Colors - Usage Limits

```
✅ DO: Accents, borders, icons, highlights
❌ DON'T: Large text blocks, backgrounds, body text
```

---

## 13. Custom Window (Platform-Specific)

### macOS/Windows Custom Titlebar

```yaml
dependencies:
  bitsdojo_window: ^0.1.6
```

### Implementation

```dart
// main.dart
import 'package:bitsdojo_window/bitsdojo_window.dart';

void main() {
  runApp(MyApp());

  doWhenWindowReady(() {
    final win = appWindow;
    win.minSize = Size(800, 700);
    win.size = Size(1000, 750);
    win.alignment = Alignment.center;
    win.title = "MP3 Yap";
    win.show();
  });
}

// Custom Titlebar Widget
class CustomTitleBar extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return WindowTitleBarBox(
      child: Container(
        color: Color(0xFF0A0A0F),
        child: Row(
          children: [
            Expanded(child: MoveWindow()),
            WindowButtons(),
          ],
        ),
      ),
    );
  }
}

class WindowButtons extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        MinimizeWindowButton(colors: _buttonColors),
        MaximizeWindowButton(colors: _buttonColors),
        CloseWindowButton(colors: _closeButtonColors),
      ],
    );
  }

  final _buttonColors = WindowButtonColors(
    iconNormal: Color(0xFF0ABDC6),
    mouseOver: Color(0xFF1B1B2A),
    mouseDown: Color(0xFF091833),
    iconMouseOver: Color(0xFFEA00D9),
  );

  final _closeButtonColors = WindowButtonColors(
    iconNormal: Color(0xFF0ABDC6),
    mouseOver: Color(0xFFFF007A),
    mouseDown: Color(0xFFEA00D9),
    iconMouseOver: Colors.white,
  );
}
```

### Design for Custom Titlebar

```
┌─────────────────────────────────────────────────────┐
│ ● ● ●                MP3 Yap              ─ □ ✕ │
│ (drag area)          (centered title)    (buttons) │
├─────────────────────────────────────────────────────┤
│                                                     │
│                   App Content                       │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## 14. Implementation Phases

### Phase 1: Foundation (Öncelikli)
- [ ] Dark theme colors
- [ ] Custom fonts (Inter, Orbitron)
- [ ] Basic glassmorphism cards
- [ ] Neon accent buttons

### Phase 2: Animations
- [ ] Page transitions
- [ ] Button hover effects
- [ ] Loading states (pulse)
- [ ] Nav bar animations

### Phase 3: Background Effects
- [ ] Gradient background
- [ ] Particle network (optional)
- [ ] Grid pattern overlay

### Phase 4: Polish
- [ ] Custom titlebar (bitsdojo_window)
- [ ] Performance mode toggle
- [ ] Scan lines effect (subtle)
- [ ] Micro-interactions

---

## 15. Review Score

**Değerlendirme:** 9/10

**Güçlü Yönler:**
- Net ve tutarlı vizyon
- Mükemmel renk kontrastı
- Modern UI teknikleri
- Teknik uygulanabilirlik

**İyileştirme Alanları:**
- Performans optimizasyonu gerekli
- Accessibility balance
- Custom window implementation

---

## Sources & Inspiration

- [Retro-futuristic UX designs - LogRocket](https://blog.logrocket.com/ux-design/retro-futuristic-ux-designs-bringing-back-the-future/)
- [UI Design Trends 2025 - Caltech](https://pg-p.ctme.caltech.edu/blog/ui-ux/top-ui-design-trends)
- [16 Trending UI Design Styles - Medium](https://medium.com/@thisara2000shehankavinda/exploring-16-trending-ui-design-styles-for-2025-322dfa4b57c2)
- [Cyberpunk Color Palettes - ColorMagic](https://colormagic.app/palette/explore/cyberpunk)
- [Flutter Background Effects - Flutter Gems](https://fluttergems.dev/effects-gradients-shaders/)
- [Glassmorphism UI - Flutter Gems](https://fluttergems.dev/glassmorphic-ui/)
- [Animated Backgrounds in Flutter](https://flutterassets.com/animated-backgrounds-in-flutter-with-examples/)
- [Cyberpunk UI - Dribbble](https://dribbble.com/tags/cyberpunk-ui)
- [Glassmorphism Examples](https://superdevresources.com/glassmorphism-ui-inspiration/)

---

*Son Güncelleme: Kasım 2025*
