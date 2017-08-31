using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;

using BitflyerApi;
using System.Net;

namespace bfOrderBook
{
    public partial class Form1 : Form
    {

        BitflyerClient client;
        Board board;
        List<double> amounts;

        bool mask = false;
        int SMAX = 0;

        String[] ss = new string[] {
                    "",
                    " ",
                    "  ",
                    "   ",
                    "    ",
                    "     ",
                    "      ",
                    "       ",
                    "        ",
                    "         "};

        String s19 = new string(' ', 19);
        String s46 = new string(' ', 46);
        String sc = ":";

        public Form1()
        {
            InitializeComponent();

            client = new BitflyerClient("", "", ProductCode.FX_BTC_JPY);
        }

        async Task getOrderBook()
        {

            List<string> orderBookA = null;
            List<string> orderBookB = null;
            List<string> orderBook = null;
            amounts = null;

            bool first = true;

            listBox1.Items.Add("Connecting to BitFlyer server ...");


            while (true)
            {
                if (!first)
                {
                    if (listBox1.DataSource.Equals(orderBookA))
                    {
                        orderBook = orderBookB;
                    }
                    else
                    {
                        orderBook = orderBookA;
                    }
                    orderBook.Clear();
                    amounts.Clear();
                }

                try
                {
                    board = await client.GetBoard();
                }
                catch (Exception ex)
                {
                    listBox1.BeginUpdate();
                    listBox1.DataSource = null;
                    listBox1.Items.Add("Connecting to BitFlyer server ...");
                    listBox1.Items.Add(ex);
                    listBox1.EndUpdate();

                    Console.WriteLine(ex);

                    first = true;

                    await Task.Delay(1000);
                    continue;
                }

                if (first)
                {
                    SMAX = Math.Max(board.Asks.Count, board.Bids.Count) + 50;

                    orderBookA = new List<string>(SMAX * 2 + 1);
                    orderBookB = new List<string>(SMAX * 2 + 1);
                    orderBook = orderBookA;

                    amounts = new List<double>(SMAX * 2 + 1);
                }


                int n = SMAX - board.Asks.Count;
                for (int i = 0; i < n; i++)
                {
                    String index = (SMAX - i).ToString();
                    orderBook.Add(ss[4 - index.Length] + index + sc);
                    amounts.Add(0.1);
                }

                for (int i = (0 < n ? board.Asks.Count : SMAX) - 1; 0 <= i; i--)
                {
                    String index = (i + 1).ToString();
                    String[] ask = board.Asks[i].Size.ToString().Split('.');
                    String pr = board.Asks[i].Price.ToString();

                    orderBook.Add(ss[4 - index.Length] + index + sc +
                        ss[5 - ask[0].Length] + ask[0] + (ask.Length == 2 ? ("." + ask[1] + ss[8 - ask[1].Length]) : ss[9]) +
                        ss[9 - pr.Length] + pr);

                    amounts.Add(board.Asks[i].Size);
                }


                String p = board.MiddlePrice.ToString();
                orderBook.Add(s19 + ss[9 - p.Length] + p + 
                    ss[6] + "spread: " + Math.Round(100 * (board.Asks[0].Price - board.Bids[0].Price) / board.MiddlePrice, 5).ToString() + " %");
                amounts.Add(0);


                n = SMAX - board.Bids.Count;
                for (int i = 0; i < (0 < n ? board.Bids.Count : SMAX); i++)
                {
                    String index = (i + 1).ToString();
                    String[] bid = board.Bids[i].Size.ToString().Split('.');
                    String pr = board.Bids[i].Price.ToString();

                    orderBook.Add(s19 +
                        ss[9 - pr.Length] + pr + ss[2] +
                        ss[5 - bid[0].Length] + bid[0] + (bid.Length == 2 ? ("." + bid[1] + ss[8 - bid[1].Length]) : ss[9]) +
                        ss[2] + sc + ss[4 - index.Length] + index);

                    amounts.Add(-1 * board.Bids[i].Size);
                }

                for (int i = 0; i < n; i++)
                {
                    String index = (board.Bids.Count + i + 1).ToString();
                    orderBook.Add(s46 + sc + ss[4 - index.Length] + index);
                    amounts.Add(-0.1);
                }


                int foc = listBox1.SelectedIndex;
                int pos = listBox1.TopIndex;

                if (!mask)
                {
                    listBox1.BeginUpdate();
                    listBox1.DataSource = orderBook;
                    listBox1.EndUpdate();
                }

                if (listBox1.DataSource == null)
                {
                    await Task.Delay(1000);
                    continue;
                }

                listBox1.SelectedIndex = foc;
                listBox1.TopIndex = pos;

                if (first)
                {
                    listBox1.TopIndex = SMAX - 20;
                    first = false;
                }

                await Task.Delay(1000);
            }
        }


        private void listBox1_MouseCaptureChanged(object sender, EventArgs e)
        {
            mask = !mask;
        }

        private void listBox1_MouseClick(object sender, MouseEventArgs e)
        {
            mask = false;
        }

        private void listBox1_MouseUp(object sender, MouseEventArgs e)
        {
            mask = false;
        }

        private void listBox1_MouseDown(object sender, MouseEventArgs e)
        {
            mask = false;
        }

        private void textBox1_TextChanged(object sender, EventArgs e)
        {
            if(listBox1.DataSource == null)
            {
                return;
            }

            if (Int32.TryParse(textBox1.Text, out int numValue))
            {
                if (board.MiddlePrice == numValue)
                {
                    listBox1.SelectedIndex = SMAX;
                    listBox1.TopIndex = listBox1.SelectedIndex - 20;
                }
                else if (board.MiddlePrice < numValue)
                {
                    for (int i = 0; i < board.Asks.Count; i++)
                    {
                        if (numValue < board.Asks[i].Price)
                        {
                            listBox1.SelectedIndex = SMAX - i;
                            listBox1.TopIndex = listBox1.SelectedIndex - 20;

                            break;
                        }
                    }
                }
                else
                {
                    for (int i = 0; i < board.Bids.Count; i++)
                    {
                        if (board.Bids[i].Price < numValue)
                        {
                            listBox1.SelectedIndex = SMAX + i;
                            listBox1.TopIndex = listBox1.SelectedIndex - 20;

                            break;
                        }
                    }
                }
            }
        }

        private async void Form1_Load(object sender, EventArgs e)
        {
            await getOrderBook();
        }

        private void button1_Click(object sender, EventArgs e)
        {
            if (listBox1.DataSource == null)
            {
                return;
            }

            listBox1.SelectedIndex = SMAX;
            listBox1.TopIndex = listBox1.SelectedIndex - 20;
        }

        private void listBox1_DrawItem(object sender, DrawItemEventArgs e)
        {
            e.DrawBackground();

            if (-1 < e.Index)
            {
                if (amounts != null && e.Index < amounts.Count) {

                    Brush b = null;

                    double a = Math.Abs(amounts[e.Index]);

                    if ((e.State & DrawItemState.Selected) != DrawItemState.Selected)
                    {

                        Brush bb = null;
                        if (0 < amounts[e.Index])
                        {
                            bb = new SolidBrush(Color.LavenderBlush);
                        }
                        else if (amounts[e.Index] < 0)
                        {
                            bb = new SolidBrush(Color.AliceBlue);
                        }
                        if (bb != null)
                        {
                            e.Graphics.FillRectangle(bb, e.Bounds);
                            bb.Dispose();
                        }

                        if (100.0 <= a)
                        {
                            b = new SolidBrush(Color.Red);
                        }
                        else if (10.0 <= a)
                        {
                            b = new SolidBrush(Color.Green);
                        }
                        else if (1.0 <= a)
                        {
                            b = new SolidBrush(Color.Blue);
                        }
                        else
                        {
                            b = new SolidBrush(e.ForeColor);
                        }
                    }
                    else
                    {
                        b = new SolidBrush(e.ForeColor);
                    }

                    e.Graphics.DrawString(((ListBox)sender).Items[e.Index].ToString(), e.Font, b, e.Bounds);
                    b.Dispose();
                }
                else
                {
                    e.Graphics.DrawString(((ListBox)sender).Items[e.Index].ToString(), e.Font, new SolidBrush(e.ForeColor), e.Bounds);
                }

            }

            e.DrawFocusRectangle();
        }
    }
}
