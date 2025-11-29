import 'package:flutter/material.dart';

class MediaItemCard extends StatelessWidget {
  final String title;
  final VoidCallback? onTap;
  final List<Widget> metadata;
  final List<Widget> actions;
  final IconData leadingIcon;
  final Color? leadingIconColor;

  const MediaItemCard({
    super.key,
    required this.title,
    this.onTap,
    this.metadata = const [],
    this.actions = const [],
    this.leadingIcon = Icons.music_note,
    this.leadingIconColor,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
          child: Row(
            children: [
              // Left side: Title and metadata
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Title row
                    Row(
                      children: [
                        Icon(
                          leadingIcon,
                          color: leadingIconColor ?? colorScheme.primary,
                          size: 18,
                        ),
                        const SizedBox(width: 6),
                        Expanded(
                          child: Text(
                            title,
                            style: theme.textTheme.titleSmall?.copyWith(
                              fontWeight: FontWeight.w600,
                            ),
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                          ),
                        ),
                      ],
                    ),
                    if (metadata.isNotEmpty) ...[
                      const SizedBox(height: 6),
                      // Metadata row
                      Wrap(
                        spacing: 12,
                        runSpacing: 4,
                        children: metadata,
                      ),
                    ],
                  ],
                ),
              ),
              // Right side: Action buttons
              if (actions.isNotEmpty)
                Row(
                  mainAxisSize: MainAxisSize.min,
                  children: actions,
                ),
            ],
          ),
        ),
      ),
    );
  }
}

class MediaMetadataItem extends StatelessWidget {
  final IconData icon;
  final String text;
  final Color? color;

  const MediaMetadataItem({
    super.key,
    required this.icon,
    required this.text,
    this.color,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final itemColor = color ?? theme.colorScheme.onSurfaceVariant;

    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Icon(icon, size: 14, color: itemColor),
        const SizedBox(width: 4),
        Text(
          text,
          style: TextStyle(
            fontSize: 12,
            color: itemColor,
          ),
        ),
      ],
    );
  }
}
