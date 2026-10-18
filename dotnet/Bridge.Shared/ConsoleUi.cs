using System.Text;

namespace Bridge.Shared;

/// <summary>
/// Console formatting helpers shared by both lab apps.
///
/// <para>
/// Kept intentionally tiny: the labs print a <i>narrative</i> (what was sent, what came back,
/// what it cost, which retries fired) because the point is to watch the mechanism, not to build
/// a UI. Colours are opt-out via <c>NO_COLOR</c> so output is pasteable into a report.
/// </para>
/// </summary>
public static class ConsoleUi
{
    private static readonly bool Colour = !string.Equals(
        Environment.GetEnvironmentVariable("NO_COLOR"), "1", StringComparison.Ordinal);

    public static void Title(string text)
    {
        Write(ConsoleColor.Cyan, $"=== {text} ===");
        Console.WriteLine();
    }

    public static void Section(string text)
    {
        Write(ConsoleColor.DarkCyan, $"-- {text}");
    }

    public static void Info(string text) => Console.WriteLine($"  {text}");

    public static void Dim(string text) => Write(ConsoleColor.DarkGray, $"  {text}");

    public static void Good(string text) => Write(ConsoleColor.Green, $"  {text}");

    public static void Bad(string text) => Write(ConsoleColor.Red, $"  {text}");

    public static void Warn(string text) => Write(ConsoleColor.Yellow, $"  {text}");

    public static void Pass(string name) => Write(ConsoleColor.Green, $"PASS  {name}");

    public static void Fail(string name, string detail)
    {
        Write(ConsoleColor.Red, $"FAIL  {name}");
        Console.WriteLine($"      {detail}");
    }

    public static void Rule()
    {
        Console.WriteLine(new string('-', 72));
    }

    /// <summary>Wraps text for terminal width so long model output stays readable.</summary>
    public static string Wrap(string text, int width = 100)
    {
        if (string.IsNullOrEmpty(text))
        {
            return string.Empty;
        }

        var builder = new StringBuilder();
        var column = 0;
        foreach (var word in text.Split(' '))
        {
            if (column > 0 && column + word.Length + 1 > width)
            {
                builder.AppendLine();
                column = 0;
            }
            else if (column > 0)
            {
                builder.Append(' ');
                column++;
            }

            builder.Append(word);
            column += word.Length;
        }

        return builder.ToString();
    }

    private static void Write(ConsoleColor colour, string text)
    {
        if (!Colour)
        {
            Console.WriteLine(text);
            return;
        }

        var previous = Console.ForegroundColor;
        Console.ForegroundColor = colour;
        Console.WriteLine(text);
        Console.ForegroundColor = previous;
    }
}
